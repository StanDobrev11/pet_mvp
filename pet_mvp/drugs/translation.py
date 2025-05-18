from modeltranslation.translator import register, TranslationOptions
from pet_mvp.drugs.models import Drug, Vaccine


@register(Drug)
class DrugTranslationOptions(TranslationOptions):
    fields = ('name', 'notes')


@register(Vaccine)
class VaccineTranslationOptions(TranslationOptions):
    fields = ('name', 'notes')