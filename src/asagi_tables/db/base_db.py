from typing import Iterable

class BasePlaceHolderGen:
	__slots__ = ()

	def size(self, items: Iterable) -> str:
		return self.qty(len(items))

	def qty(self, qty: int=1) -> str:
		return ','.join(self() for _ in range(qty))
