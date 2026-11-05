from django.db import models

class Department(models.Model):
    code = models.CharField('Código Dpto', max_length=2, unique=True)
    name = models.CharField('Departamento', max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Municipality(models.Model):
    code = models.CharField('Código DIVIPOLA', max_length=5, unique=True)
    name = models.CharField('Municipio', max_length=100)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='municipalities')

    def __str__(self):
        return f"{self.code} - {self.name}"


