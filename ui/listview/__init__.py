#coding:UTF-8

from typing import Any, Iterable, Mapping
from tkinter import Widget, Pack, XView, YView, Frame

class Observer:

    def update(self, object :Any):
        raise NotImplementedError("")

class Observable:

    def __init__(self) -> None:
        self._observers : list[Observer] = []
    
    @property
    def observers(self):
        return self._observers
    
    def add_observer(self, observer :Observer):
        self.observers.append(observer)
    
    def remove_observer(self, o:Observer):
        self.observers.remove(o)

    def update_observers(self, object):

        for obs in self.observers:
            obs.update(object)
            


class ListModel(Observable):
    
    def __init__(self, model = []) -> None:
        super().__init__()
        self._model : list = model
    
    def append(self, item: Any) -> None:
        self.insert(len(self._model), item)

    def insert(self, index :int, item) -> None:
        print("inserted")
        self._model.insert(index, item)
        # notify observers
        self.update_observers(self)
        
    
    def remove(self, index :int) -> None:
        if index >= len(self._model):
            raise IndexError()
        
        del self._model[index]
        # notify observer
        self.update_observers(self)
    
    def get(self, index :int):
        return self._model[index]
    

class ListItemDelegate(Frame):

    def __init__(self, master, object) -> None:
        super().__init__(master)
        self.item = object
        #self.master = master

    def delegate(self) -> Widget :
        raise NotImplementedError("")
    
    def pack(self) -> None:
        self.delegate().pack()
        super().pack()


class ListView(Frame, Observer, Pack, XView, YView):

    def __init__(self, master, model :ListModel) -> None:
        super().__init__(master)
    
        self._model : ListModel = model
        self._delegate = None

        self.content = self
        self._setup_model()
    
    @property
    def model(self) :
        return self._model
    
    def set_model(self, model : ListModel):
        self._model = model
    
    @property
    def delegate(self):
        return self._delegate
    
    def set_delegate(self, delegate :Widget):
        self._delegate = delegate

    def _setup_model(self):
        self.model.add_observer(self)
    
    def update(self, object):
        self.set_model(object)
        self._refresh()

    def _show_items(self):

        self.items = []

        for elt in self.model._model:
            item = self.delegate(self.content, elt)
            self.items.append(item)
            item.pack()
            print(self.items)
    
    def _destroy_items(self):
        
        for item in self.items:
            item.destroy()

    def _refresh(self):
        self._destroy_items()
        self._show_items()

    def pack(self):
        self._show_items()
        super().pack()