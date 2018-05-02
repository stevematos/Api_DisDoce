from django.db import models
from apps.docente.models import Docente,TipoGrado
# Create your models here.

class Programa(models.Model):
    id_programa = models.SmallIntegerField(primary_key=True)
    nom_programa = models.CharField(max_length=116)
    sigla_programa = models.CharField(max_length=10)
    id_tip_grado = models.ForeignKey(TipoGrado,on_delete=models.CASCADE,db_column='id_tip_grado')
    vigencia_programa = models.BooleanField()
    class Meta:
        managed = False
        db_table = 'programa'


class Curso(models.Model):
    id_curso = models.IntegerField(primary_key=True)
    nom_curso = models.CharField(max_length=40)
    id_programa = models.ForeignKey(Programa, db_column='id_programa',related_name='cursos',on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'curso'

class Preferencia(models.Model):
    id_preferencia = models.IntegerField(primary_key=True)
    id_docente = models.ForeignKey(Docente, db_column='id_docente', on_delete=models.CASCADE)
    id_curso = models.ForeignKey(Curso, db_column='id_curso',related_name='preferencia',on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'preferencia'

