import uuid

from django.db import models, transaction
from django.db.utils import IntegrityError
import pytest

from psqlextra.query import ConflictAction

from ..fake_model import get_fake_model


def _traditional_insert(model, random_value):
    """Performs a concurrency safe insert the
    traditional way."""

    try:
        with transaction.atomic():
            return model.objects.create(field=random_value)
    except IntegrityError:
        return model.objects.filter(field=random_value).first()


def _native_insert(model, random_value):
    """Performs a concurrency safeinsert
    using the native PostgreSQL conflict resolution."""

    return (
        model.objects
        .on_conflict(['field'], ConflictAction.NOTHING)
        .insert_and_get(field=random_value)
    )


@pytest.mark.django_db()
@pytest.mark.benchmark()
def test_traditional_insert(benchmark):
    model = get_fake_model({
        'field': models.CharField(max_length=255, unique=True)
    })

    random_value = str(uuid.uuid4())[:8]
    model.objects.create(field=random_value)

    benchmark(_traditional_insert, model, random_value)


@pytest.mark.django_db()
@pytest.mark.benchmark()
def test_native_insert(benchmark):
    model = get_fake_model({
        'field': models.CharField(max_length=255, unique=True)
    })

    random_value = str(uuid.uuid4())[:8]
    model.objects.create(field=random_value)

    benchmark(_native_insert, model, random_value)
