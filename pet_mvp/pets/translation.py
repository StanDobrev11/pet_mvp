from modeltranslation.translator import register, TranslationOptions
from pet_mvp.pets.models import Pet, Transponder, Tattoo


@register(Pet)
class PetTranslationOptions(TranslationOptions):
    fields = ('name', 'species', 'breed', 'color', 'features')


@register(Transponder)
class TransponderTranslationOptions(TranslationOptions):
    fields = ('location',)


@register(Tattoo)
class TattooTranslationOptions(TranslationOptions):
    fields = ('location',)