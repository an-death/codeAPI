from app import db


class MetaModel:
    def __repr__(self, **kwargs):
        class_name = self.__class__.__name__
        return f'<{class_name}: {" ".join(map(":".join, kwargs.items()))}>'


class Model(db.Model, MetaModel):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    class Meta:
        repr_fields = ['id']

    def __repr__(self):
        kwargs = {field: str(getattr(self, field)) for field in self.Meta.repr_fields}
        return super().__repr__(**kwargs)

    def __str__(self):
        return f'"{getattr(self, self.Meta.repr_fields[0])}"'

