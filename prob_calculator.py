class ProbCalculator:
    def __init__(self) -> None:
        pass
        #self.character = character

    def make(self, character):
        return self._make(character)

    def _make(self, character):
        _prob = 1
        for group in character.factory.groups:
            for _attr in group.active:
                _prob *= _attr.prob

        _prob *= character.body.color_gen.rarity
        return _prob