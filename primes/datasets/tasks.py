from celery import shared_task, chain
from primes import celery_app

from .models import Processing, Dataset
from .exceptions import DatasetInputError

# Test function chain #
def process_datasets(query_set):
    """
    Process each item of the given QuerySet.
    :param query_set: QuestySet of Dataset objects
    :return: None
    """

    # create Processing object in order to assign dataset to it
    processing = Processing.objects.create()

    for dataset in query_set:
        # Chaining three tasks with Celery chain
        chain_result = chain(first_select_json_from_dataset.s((dataset.pk, processing.pk)),
                             second_test_function.s(),
                             third_save_json_to_db.s()).apply_async()

    return processing.pk

# main tasks

# Since Celery is a distributed system, you can't know in which process,
# or even on what machine the task will run. So you shouldn't pass
# Django model objects as arguments to tasks, its almost always better to
# re-fetch the object from the database instead, as there are possible
# race conditions involved.

@shared_task
def first_select_json_from_dataset(dataset_and_processing_pks):
    """
    Pass a JSON from Dataset model for a given dataset to a test function.

    :param dataset_and_processing_pks: tuple of two (Dataset PK, Processing PK)
    :return: tuple of two (Dataset PK; Processing PK)
    """
    # unpack tuple; needed for Celery chain compatibility
    dataset_pk, processing_pk = dataset_and_processing_pks

    # re-fetch Dataset and Processing from DB
    dataset = Dataset.objects.get(pk=dataset_pk)
    processing = Processing.objects.get(pk=processing_pk)



    # mark dataset belonging to the given Processing item
    dataset.processing = processing

    # save dataset
    dataset.save()

    # if dataset got an exception on submission,
    # mark related processing having exceptions,
    # raise an error, so that further execution of the chain stops
    if dataset.exception:
        processing.exceptions = True
        processing.save()
        raise DatasetInputError('Submitted dataset has got an exception')

    return dataset.pk, processing.pk


@shared_task
def second_test_function(dataset_and_processing_pks):
    """
    Pass a result of JSON processing to a function that saves result on a model.

    :param dataset_and_processing_pks: tuple of two (Dataset PK, Processing PK)
    :return: tuple of two (Dataset PK; JSON (Python's list of dicts))
    """
    # unpack tuple; needed for Celery chain compatibility
    dataset_pk, processing_pk = dataset_and_processing_pks

    # re-fetch Dataset and Processing
    dataset = Dataset.objects.get(pk=dataset_pk)
    processing = Processing.objects.get(pk=processing_pk)

    result = []
    # calculate result; handle exceptions
    try:
        result = [{'result': pair['a'] + pair['b']} for pair in dataset.data]
    except Exception as err:
        # exception string = exception type + exception args
        exception_message = "{type}: {message}". \
            format(type=type(err).__name__, message=err)
        # save exception to db
        dataset.exception = exception_message
        processing.exceptions = True

    dataset.save()
    processing.save()

    return dataset_pk, result


@shared_task
def third_save_json_to_db(dataset_pk_and_json):
    """
    Save input JSON on a model.

    :param dataset_pk_and_json: tuple of two (Dataset PK, JSON (Python's list of dicts))
    :return: boolean: True if data saved to the data base, False otherwise
    """
    # unpack tuple; needed for Celery chain compatibility
    dataset_pk, json_data = dataset_pk_and_json

    # re-fetch Dataset and Processing
    dataset = Dataset.objects.get(pk=dataset_pk)

    # save results to the DB
    dataset.result = json_data
    dataset.save()

    return not dataset._state.adding
