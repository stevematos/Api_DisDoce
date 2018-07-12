import datetime
import time
import json
from django.shortcuts import render
from django.conf import settings
from reportlab.lib.utils import ImageReader
from rest_framework import status,generics
from rest_framework.views import APIView
from apps.docente.serializers import DocenteSerializer
from rest_framework.response import Response
from apps.docente.models import Docente,DatosAcademicos,TipoGrado
from apps.disponibilidad.models import Disponibilidad, Dia
from apps.curso.models import Preferencia, Curso, Ciclo
from django.http import  HttpResponse
from reportlab.pdfgen import canvas
from Algoritmos.libreria_pdf import *
from Algoritmos.Algoritmos_Disponibilidad import devolver_disponibilidad,docente_dias_disponibilidad,docente_horas_disponibilidad
from reportlab.lib.pagesizes import letter,landscape
from reportlab.platypus import Table,TableStyle
from PIL import Image
# Create your views here.



class DocenteGet(APIView):
    serializer = DocenteSerializer
    def get(self, request, id):
        try:
            lista = Docente.objects.get(id=id)
        except Docente.DoesNotExist:
            return Response('NO EXISTE DOCENTE',status=status.HTTP_400_BAD_REQUEST)
        listajson=(self.serializer(lista)).data
        listaDatos_Academicos=DatosAcademicos.objects.filter(id_docente=id)
        for datos_academicos in listaDatos_Academicos:
            listajson[datos_academicos.id_tip_grado.nom_tip_grado]=datos_academicos.mencion_grado
        return Response(listajson)

class PDFView(APIView):
    def get(self, request, id, idciclo):
        response = HttpResponse(content_type='application/pdf')
        nombre_pdf='docente'+id
        response['Content-Disposition'] = 'filename="'+nombre_pdf+'.pdf"'

        try:
            informacion_docente=Docente.objects.get(id=id)
        except Docente.DoesNotExist:
            return Response('NO EXISTE DOCENTE',status=status.HTTP_400_BAD_REQUEST)

        #año del sistema
        #ahora = datetime.datetime.now()

        #variables docente
        docente_nom=informacion_docente.nombres
        apellidos=informacion_docente.apell_pat+" "+informacion_docente.apell_mat
        docente_ape = apellidos
        docente_codigo = informacion_docente.codigo
        docente_tipo_documento=informacion_docente.tipo_document
        docente_nro_documento= informacion_docente.nro_document
        docente_email = informacion_docente.email
        docente_celular=informacion_docente.celular
        docente_genero= informacion_docente.genero
        #docente_pagina_web= informacion_docente.pag_web
        docente_fecha_nac= informacion_docente.fecha_nac
        docente_pais= informacion_docente.pais
        docente_direccion= informacion_docente.direccion
        #docente_sunedu_le= informacion_docente.sunedu_ley
        #docente_categoria= informacion_docente.categoria
        #docente_regimen_dedicacion= informacion_docente.regimen_dedicacion
        #docente_cv = informacion_docente.cv
        foto_docente=None
        docente_foto=ImageReader(foto_docente) if foto_docente else settings.IMAGENES +'/profesor.jpg'

        #disponibilidadocente
        total_dias_disponible=docente_dias_disponibilidad(id, idciclo)
        total_horas_disponible=docente_horas_disponibilidad(id, idciclo)


        total_datos_academicos = DatosAcademicos.objects.filter(id_docente=id).values()
        docente_Grado={}
        for datos_academicos in total_datos_academicos:
            Nombre_Tipo_Grado=(TipoGrado.objects.get(id_tip_grado=datos_academicos['id_tip_grado_id'])).nom_tip_grado
            Nombre_Mencion_Grado=datos_academicos['mencion_grado']
            docente_Grado[Nombre_Tipo_Grado]=Nombre_Mencion_Grado

        #variabls de ayuda para pintar docente
        fin_direccion=25
        direccion_caracter_siguiente_linea=''

        # variabls de ayuda para pintar programa de los cursos
        fin_programa_curso=55
        programa_curso_caracter_siguiente_linea=''

        # variabls de ayuda para pintar programa de los cursos
        fin_marco_curso = 60
        marco_curso_caracter_siguiente_linea = '-'

        #obtener ciclo
        ciclo=''
        try:
            ciclo = Ciclo.objects.get(id_ciclo=idciclo)
        except Ciclo.DoesNotExist:
            return Response('NO EXISTE CICLO', status=status.HTTP_400_BAD_REQUEST)
        
        if docente_direccion:
            if len(docente_direccion)>=fin_direccion :
                if docente_direccion[fin_direccion]!=' ':
                    direccion_caracter_siguiente_linea='-'


        docente_genero_radio = {'Masculino':False,'Femenino':False}

        if docente_genero=='M' :
            docente_genero_radio['Masculino']=True
        elif docente_genero=='F':
            docente_genero_radio['Femenino']=True

        p = canvas.Canvas(response)
        p.setTitle(docente_nom+' '+apellidos)

        #variables globales
        ancho_pagina,alto_pagina=letter
        espacio_medio_left_right=6
        extra_informacion_personal=20
        alto_informacion_personal=185 - extra_informacion_personal
        y_informacion_personal=285 + extra_informacion_personal
        extra_informacion_academica = 20
        alto_informacion_academica=150 - extra_informacion_academica
        y_informacion_academica=100 + extra_informacion_academica
        x_form_variable=20

        #variables:FORMULARIO TOTAL
        titulo_tipo_letra_form='Times-Bold'
        titulo_tamanio_letra_form=16

        titulo_medio_tipo_letra_form = 'Times-Bold'
        titulo_medio_tamanio_letra_form = 16

        campo_tipo_letra_form = 'Times-Bold'
        campo_tamanio_letra_form = 10

        valor_tipo_letra_form= 'Times-Roman'
        valor_tamanio_letra_form = 10

        campo_radio_tipo_letra_form = 'Times-Bold'
        campo_radio_tamanio_letra_form = 10

        radio_tipo_letra_form = 'Times-Roman'
        radio_tamanio_letra_form = 10
        radio_longitud_radio=2
        radio_espacio_nombre=15

        switcher_formulario = {
            'titulo': titulo,
            'campo': campo,
            'campo_radio': campo,
            'campo_sgt': campo,
            'radio': radio,
            'linea':linea,
            'titulo_medio':titulo_medio,
            'valor': campo,
            'valor_x_variable':valor_x_variable,
        }
        switcher_salto_linea = {
            'titulo': 20,
            'campo': 0,
            'campo_sgt': 20,
            'campo_radio':0,
            'radio': 20,
            'titulo_medio': 30,
            'valor': 20,
            'linea' : 20,
            'valor_x_variable': 20,
        }

        switcher_padding_left = {
            'campo': 0,
            'campo_sgt': 0,
            'radio': 100,
            'campo_radio': 0,
            'valor': 100,
        }

        #variables:titulo1
        tamanio_letra_titulo1=19
        texto_titulo1='INFORMACION DEL DOCENTE' #ANTES DISPONIBILIDAD DEL DOCENTE
        tipo_letra_titulo1='Times-Bold'
        cantidad_pixeles_titulo1=295
        padding_titulo_bottom_top_titulo1=15
        padding_titulo_left_right_titulo1=130
        x_titulo1=ancho_pagina/2-cantidad_pixeles_titulo1/2
        y_titulo1=800


        #variables:titulo1_1
        tamanio_letra_titulo1_1=17
        texto_titulo1_1 ='Informacion personal'
        tipo_letra_titulo1_1='Times-Bold'
        cantidad_pixeles_titulo1_1=155
        padding_titulo_bottom_top_titulo1_1=10
        padding_titulo_left_right_titulo1_1=180
        x_titulo1_1 = ancho_pagina/2-cantidad_pixeles_titulo1_1/2
        y_titulo1_1 = 490

        #variables:titulo1_2
        tamanio_letra_titulo1_2=17
        texto_titulo1_2 = 'Informacion academica'
        tipo_letra_titulo1_2='Times-Bold'
        cantidad_pixeles_titulo1_2=150
        padding_titulo_bottom_top_titulo1_2=10
        padding_titulo_left_right_titulo1_2=185
        x_titulo1_2 = ancho_pagina/2-cantidad_pixeles_titulo1_2/2
        y_titulo1_2 = 268

        #variables:Imagen
        x_imagen=60
        y_imagen=530
        ancho_porcentaje_imagen=29
        alto_porcentaje_imagen=29

        #variables:informacion_basica form
        ancho_informacion_basica=250
        alto_informacion_basica=235
        x_informacion_basica=ancho_pagina/2+espacio_medio_left_right
        y_informacion_basica=530
        x_form_informacion_basica=x_informacion_basica+x_form_variable
        y_form_informacion_basica=y_informacion_basica+alto_informacion_basica*(7/ 8)

        lista_form_informacion_basica = [
            {'campo': {'text': 'Nombres',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_nom,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Apellidos',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_ape,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Fecha',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': time.strftime("%d/%m/%y"),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Total de horas',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': str(total_horas_disponible),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Ciclo',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': ciclo.nom_ciclo,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
        ]


        #variables:informacion_personal1 form
        ancho_informacion_personal1=250
        alto_informacion_personal1=alto_informacion_personal
        x_informacion_personal1=ancho_pagina/2-ancho_informacion_personal1-espacio_medio_left_right
        y_informacion_personal1=y_informacion_personal
        x_form_informacion_personal1 = x_informacion_personal1 +x_form_variable
        y_form_informacion_personal1 = y_informacion_personal1 + alto_informacion_personal1 * (7 / 8)

        lista_form_informacion_personal1 = [
            {'campo': {'text': 'Nombres',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_nom,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Apellidos',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_ape,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': docente_tipo_documento,
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_nro_documento,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo_radio': {'text': 'Sexo',
                             'tipo_letra': campo_radio_tipo_letra_form,
                             'tamanio_letra': campo_radio_tamanio_letra_form}},
            {'radio': {'text': 'Masculino',
                       'tipo_letra': radio_tipo_letra_form,
                       'radio': radio_longitud_radio,
                       'Marcado': docente_genero_radio,
                       'espacio_nombre': radio_espacio_nombre,
                       'tamanio_letra': radio_tamanio_letra_form}},
            {'radio': {'text': 'Femenino',
                       'tipo_letra': radio_tipo_letra_form,
                       'radio': radio_longitud_radio,
                       'Marcado': docente_genero_radio,
                       'espacio_nombre': radio_espacio_nombre,
                       'tamanio_letra': radio_tamanio_letra_form}},
            {'campo': {'text': 'Correo',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_email,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
        ]

        #variables:informacion_personal2 form
        ancho_informacion_personal2 = 250
        alto_informacion_personal2 = alto_informacion_personal
        x_informacion_personal2 = ancho_pagina/2+espacio_medio_left_right
        y_informacion_personal2 = y_informacion_personal
        x_form_informacion_personal2 = x_informacion_personal2 + x_form_variable
        y_form_informacion_personal2 = y_informacion_personal2 + alto_informacion_personal2 * (7 / 8)

        lista_form_informacion_personal2 = [
            {'campo': {'text': 'Fecha de Nacimiento',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_fecha_nac.strftime('%m/%d/%Y'),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Lugar de Nacimiento',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_pais,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Direccion',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_direccion[:fin_direccion]+direccion_caracter_siguiente_linea,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'valor': {'text': docente_direccion[fin_direccion:],
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Celular',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_celular,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
        ]
        # variables:informacion_academica1 form
        ancho_informacion_academica1 = 250
        alto_informacion_academica1 = alto_informacion_academica
        x_informacion_academica1 = ancho_pagina/2-ancho_informacion_academica1-espacio_medio_left_right
        y_informacion_academica1 = y_informacion_academica
        x_form_informacion_academica1 = x_informacion_academica1 +x_form_variable
        y_form_informacion_academica1 = y_informacion_academica1 + alto_informacion_academica1 * (7 / 8)

        lista_form_informacion_academica1 = [
            {'campo': {'text': 'Codigo',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_codigo,
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'titulo': {'text': 'GRADOS',
                        'tipo_letra': titulo_tipo_letra_form,
                        'tamanio_letra': titulo_tamanio_letra_form}},
            {'campo': {'text': 'Titulo Profesional',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_Grado.get('Titulo','NO TIENE'),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Licenciatura',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_Grado.get('Licenciatura', 'NO TIENE'),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
        ]

        # variables:informacion_academica2 form
        ancho_informacion_academica2 = 250
        alto_informacion_academica2 = alto_informacion_academica
        x_informacion_academica2 = ancho_pagina/2+espacio_medio_left_right
        y_informacion_academica2 = y_informacion_academica
        x_form_informacion_academica2 = x_informacion_academica2 +x_form_variable
        y_form_informacion_academica2 = y_informacion_academica2 + alto_informacion_academica2 * (7 / 8)

        lista_form_informacion_academica2 = [
            {'titulo': {'text': 'POSGRADOS',
                        'tipo_letra': titulo_tipo_letra_form,
                        'tamanio_letra': titulo_tamanio_letra_form}},
            {'campo': {'text': 'Maestria',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_Grado.get('Maestria', 'NO TIENE'),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Especialidad',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_Grado.get('Especialidad', 'NO TIENE'),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Doctorado',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor': {'text': docente_Grado.get('Doctorado', 'NO TIENE'),
                       'tipo_letra': valor_tipo_letra_form,
                       'tamanio_letra': valor_tamanio_letra_form}},
        ]
        #titulo1
        titulo_texto(p,texto_titulo1,x_titulo1,y_titulo1,
               tipo_letra_titulo1,tamanio_letra_titulo1,
               padding_titulo_left_right_titulo1,padding_titulo_bottom_top_titulo1,cantidad_pixeles_titulo1)

        #imagen profesor
        dibujar_imagen(p,docente_foto,
                       x_imagen,
                       y_imagen,
                       ancho_porcentaje_imagen,
                       alto_porcentaje_imagen)

        #informacion_basica
        p.rect(x_informacion_basica,y_informacion_basica,ancho_informacion_basica,alto_informacion_basica)
        formulario(p,x_form_informacion_basica,y_form_informacion_basica,lista_form_informacion_basica,switcher_formulario,switcher_salto_linea
                   ,switcher_padding_left)

        #titulo1_1
        titulo_texto(p,texto_titulo1_1,x_titulo1_1,y_titulo1_1,
               tipo_letra_titulo1_1,tamanio_letra_titulo1_1,
               padding_titulo_left_right_titulo1_1,padding_titulo_bottom_top_titulo1_1,cantidad_pixeles_titulo1_1)

        #informacion_personal1
        p.rect(x_informacion_personal1,y_informacion_personal1,ancho_informacion_personal1,alto_informacion_personal1)
        formulario(p,x_form_informacion_personal1,y_form_informacion_personal1,
                   lista_form_informacion_personal1,switcher_formulario,
                   switcher_salto_linea
                   ,switcher_padding_left)

        #informacion_personal2
        p.rect(x_informacion_personal2,y_informacion_personal2,ancho_informacion_personal2,alto_informacion_personal2)
        formulario(p,x_form_informacion_personal2,y_form_informacion_personal2,
                   lista_form_informacion_personal2,switcher_formulario,
                   switcher_salto_linea
                   ,switcher_padding_left)

        # titulo1_2
        titulo_texto(p, texto_titulo1_2, x_titulo1_2, y_titulo1_2,
                     tipo_letra_titulo1_2, tamanio_letra_titulo1_2,
                     padding_titulo_left_right_titulo1_2, padding_titulo_bottom_top_titulo1_2,
                     cantidad_pixeles_titulo1_2)

        # informacion_academica1
        p.rect(x_informacion_academica1, y_informacion_academica1, ancho_informacion_academica1,
               alto_informacion_academica1)
        formulario(p, x_form_informacion_academica1, y_form_informacion_academica1,
                   lista_form_informacion_academica1, switcher_formulario,
                   switcher_salto_linea
                   , switcher_padding_left)

        # informacion_academica2
        p.rect(x_informacion_academica2, y_informacion_academica2, ancho_informacion_academica2,
               alto_informacion_academica2)
        formulario(p, x_form_informacion_academica2, y_form_informacion_academica2,
                   lista_form_informacion_academica2, switcher_formulario,
                   switcher_salto_linea
                   , switcher_padding_left)

        p.showPage()

        #                   OTRA PAGINA

        #variables:titulo2
        tamanio_letra_titulo2=tamanio_letra_titulo1
        texto_titulo2 = 'PREFERENCIA DE CURSOS'
        tipo_letra_titulo2= tipo_letra_titulo1
        cantidad_pixeles_titulo2=270
        padding_titulo_bottom_top_titulo2=padding_titulo_bottom_top_titulo1
        padding_titulo_left_right_titulo2=padding_titulo_left_right_titulo1
        x_titulo2 = ancho_pagina/2-cantidad_pixeles_titulo2/2
        y_titulo2 = y_titulo1

        #variables:Marco
        margin_marco_left_right=41
        margin_marco_bottom_top=30
        x_marco=margin_marco_left_right
        y_marco=margin_marco_bottom_top
        ancho_marco=ancho_pagina-2*margin_marco_left_right
        alto_marco=alto_pagina-2*margin_marco_bottom_top


        #variables:Marcos
        margin_marcos_left_right=40
        margin_marcos_top_bottom =50
        separacion_marcos=40
        x_marcos=x_marco + margin_marcos_left_right
        y_marcos=y_marco+alto_marco-margin_marcos_top_bottom
        ancho_marcos=ancho_marco - 2 * margin_marcos_left_right

        #variables:marcos form
        padding_marcos_form_left= 20
        padding_marcos_top_bottom = 20
        x_form_marcos=x_marcos+padding_marcos_form_left

        # titulo2
        titulo_texto(p, texto_titulo2, x_titulo2, y_titulo2,
                     tipo_letra_titulo2, tamanio_letra_titulo2,
                     padding_titulo_left_right_titulo2, padding_titulo_bottom_top_titulo2,
                     cantidad_pixeles_titulo2)

        #Marco
        p.rect(x_marco,y_marco,ancho_marco,alto_marco)


        #Algoritmos

        #Devovler cursos x programa
        preferencias = Preferencia.objects.filter(id_docente=id, id_ciclo=idciclo).values()
        cursos=[]
        programas_cursos={}
        for preferencia in preferencias:
            curso=Curso.objects.get(id_curso=preferencia['id_curso_id'])
            """try:
                informacion_docente = Docente.objects.get(id_docente=id)
            except Docente.DoesNotExist:
                return HttpResponse('NO EXISTE DOCENTE') ver despues"""
            if curso.id_programa.nom_programa not in programas_cursos.keys() :
                programas_cursos[curso.id_programa.nom_programa]=[]
            programas_cursos[curso.id_programa.nom_programa].append(curso.nom_curso)

        #FORM_DINAMICO


        for key, value in programas_cursos.items():
            programa_curso_caracter_siguiente_linea = ' '
            if len(key) > fin_programa_curso:
                if key[fin_programa_curso] != ' ':
                    programa_curso_caracter_siguiente_linea = '-'

            lista_form_marcos_form = [
                {'campo': {'text': 'Nombre de programa:',
                            'tipo_letra': campo_tipo_letra_form,
                            'tamanio_letra': campo_tamanio_letra_form}},
                {'valor_x_variable': {'text':  key[:fin_programa_curso]+programa_curso_caracter_siguiente_linea,
                           'x_variable':100,
                           'tipo_letra': valor_tipo_letra_form,
                           'tamanio_letra': valor_tamanio_letra_form}},
                {'valor': {'text': key[fin_programa_curso:],
                           'tipo_letra': valor_tipo_letra_form,
                           'tamanio_letra': valor_tamanio_letra_form}},
                {'linea': {'x_inicio_linea': x_marcos,
                           'x_ancho_linea': ancho_marcos}},
                {'campo_sgt': {'text': 'Nombre(s) de( los) curso(s)',
                           'tipo_letra': campo_tipo_letra_form,
                           'tamanio_letra': campo_tamanio_letra_form}},
            ]

            for curso in value:
                curso="-"+curso
                faltante=len(curso)
                while(faltante>fin_marco_curso):
                    curso_text=curso[:fin_marco_curso]
                    curso=curso[fin_marco_curso:]
                    faltante=len(curso)
                    lista_form_marcos_form.append(
                        {'valor_x_variable': {'text': curso_text+marco_curso_caracter_siguiente_linea,
                                   'tipo_letra': valor_tipo_letra_form,
                                   'x_variable':40,
                                   'tamanio_letra': valor_tamanio_letra_form}},
                    )
                lista_form_marcos_form.append(
                    {'valor_x_variable': {'text': curso,
                               'tipo_letra': valor_tipo_letra_form,
                               'x_variable': 40,
                               'tamanio_letra': valor_tamanio_letra_form}},
                )
            y_form_marcos=y_marcos
            alto_marcos=0
            for lista in lista_form_marcos_form:
                for key in lista:
                    alto_marcos=alto_marcos+switcher_salto_linea.get(key,0)
            y_marcos=y_marcos-alto_marcos-separacion_marcos
            if y_marcos<0 :
                #OTRA PAGINA
                p.showPage()
                # variables:Marcos
                margin_marcos_left_right = 40
                margin_marcos_top_bottom = 50
                separacion_marcos = 40
                x_marcos = x_marco + margin_marcos_left_right
                y_marcos = y_marco + alto_marco - margin_marcos_top_bottom
                ancho_marcos = ancho_marco - 2 * margin_marcos_left_right

                # variables:marcos form

                #extra
                y_form_marcos = y_marcos

                padding_marcos_top_bottom = 20
                padding_marcos_form_left = 20
                x_form_marcos = x_marcos + padding_marcos_form_left
                # titulo2
                titulo_texto(p, texto_titulo2, x_titulo2, y_titulo2,
                             tipo_letra_titulo2, tamanio_letra_titulo2,
                             padding_titulo_left_right_titulo2, padding_titulo_bottom_top_titulo2,
                             cantidad_pixeles_titulo2)
                # Marco
                p.rect(x_marco, y_marco, ancho_marco, alto_marco)

                #extras reiniciar
                y_marcos = y_marcos - alto_marcos - separacion_marcos

            formulario(p,x_form_marcos,y_form_marcos,lista_form_marcos_form,switcher_formulario,
                        switcher_salto_linea,switcher_padding_left)
            p.rect(x_marcos,y_marcos+separacion_marcos,ancho_marcos,alto_marcos+padding_marcos_top_bottom)


        p.showPage()


        p.setPageSize(landscape(letter))
        #               OTRA PAGINA

        tamanio_letra_titulo3 = 19
        texto_titulo3 = 'DISPONIBILIDAD DE HORARIO'  # ANTES DISPONIBILIDAD DEL DOCENTE
        tipo_letra_titulo3 = 'Times-Bold'
        cantidad_pixeles_titulo3 = 295
        padding_titulo_bottom_top_titulo3 = 15
        padding_titulo_left_right_titulo3 = 130
        x_titulo3 = alto_pagina / 2 - cantidad_pixeles_titulo3 / 2
        y_titulo3 = ancho_pagina-60

        # titulo3
        titulo_texto(p, texto_titulo3, x_titulo3, y_titulo3,
                     tipo_letra_titulo3, tamanio_letra_titulo3,
                     padding_titulo_left_right_titulo3, padding_titulo_bottom_top_titulo3, cantidad_pixeles_titulo3)


        #Algoritmo Disponibilidad
        horarios_intervalos = Disponibilidad.objects.filter(id_docente=id, id_ciclo=idciclo).order_by('id_disponibilidad').values()
        array=[]
        if horarios_intervalos:
            array = devolver_disponibilidad(horarios_intervalos, 8, 14)



        #variables:Fechas
        x_dias=100
        y_dias=420
        x_dias_intervalo=60
        dias_tipo_letra = 'Times-Roman'
        dias_tamanio_letra = 12
        dias=['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo']

        i=0


        #variables:horas
        x_horas=50
        y_horas=400
        y_horas_intervalo=20
        horas_tipo_letra = 'Times-Roman'
        horas_tamanio_letra = 12

        #variables:totalxdias
        x_totalxdias = 50
        y_totalxdias = 100
        x_totalxdias_intervalo = 60
        totalxdias_tipo_letra = 'Times-Roman'
        totalxdias_tamanio_letra = 15
        totalxdias_i=0
        totalxdias=[]
        totalxdias_texto="Total"


        #Mostrar dias
        for x in range(x_dias,x_dias+x_dias_intervalo*len(dias),x_dias_intervalo):
            dia=texto(p,dias[i],x,y_dias,dias_tipo_letra,dias_tamanio_letra)
            p.drawText(dia)
            i=i+1

        y_inicial_horas=y_horas
        #Mostrar horas
        for x in range(8,22):
            hora=str(x)+"-"+str(x+1)
            dia = texto(p, hora, x_horas, y_horas, horas_tipo_letra, horas_tamanio_letra)
            y_horas=y_horas-y_horas_intervalo
            p.drawText(dia)

        Disponibilidad_marcado=True
        if not array:
            Disponibilidad_marcado=False
        for dia in range(len(dias)):
            totalxdias.append(0)
            for horas in range(14):
                if Disponibilidad_marcado and array[horas+14*dia]:
                    marcado = 1
                    totalxdias[totalxdias_i]=totalxdias[totalxdias_i]+1
                else:
                    marcado = 0
                p.rect(x_dias+dia*(x_dias_intervalo)+10,y_inicial_horas-horas*(y_horas_intervalo),10,10,1,marcado)

            totalxdias_i=totalxdias_i+1

        #mostrar total x dias
        totalxdias_i=0
        Texto_totalxdias=texto(p, totalxdias_texto, x_totalxdias, y_totalxdias, totalxdias_tipo_letra, totalxdias_tamanio_letra)
        p.drawText(Texto_totalxdias)
        x_totalxdias=x_totalxdias+x_totalxdias_intervalo

        for x in range(x_totalxdias,x_totalxdias+x_totalxdias_intervalo*len(totalxdias),x_totalxdias_intervalo):
            totalxdia=texto(p,str(totalxdias[totalxdias_i]),x,y_totalxdias,totalxdias_tipo_letra,totalxdias_tamanio_letra)
            p.drawText(totalxdia)
            totalxdias_i=totalxdias_i+1
        

        # variables:marco_horario
        x_marco_horario=x_horas-20
        y_marco_horario=y_horas
        alto_marco_horario=y_dias-y_marco_horario+30
        ancho_marco_horario=x_dias+len(dias)*x_dias_intervalo-30

        #Marco_Horario
        p.rect(x_marco_horario, y_marco_horario, ancho_marco_horario, alto_marco_horario)


        #variables:resumen
        ancho_resumen = 220
        alto_resumen = 100
        x_resumen = 550
        y_resumen = 350
        x_form_resumen = x_resumen + ancho_resumen * (1 / 8)
        y_form_resumen = y_resumen + alto_resumen * (7 / 8)-10

        lista_form_resumen = [
            {'titulo': {'text': 'RESUMEN',
                        'tipo_letra': titulo_tipo_letra_form,
                        'tamanio_letra': titulo_tamanio_letra_form}},
            {'campo': {'text': 'Toral de horas disponibles :',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor_x_variable': {'text': str(total_horas_disponible),
                                  'x_variable': 130,
                                  'tipo_letra': valor_tipo_letra_form,
                                  'tamanio_letra': valor_tamanio_letra_form}},
            {'campo': {'text': 'Toral de dias disponibles:',
                       'tipo_letra': campo_tipo_letra_form,
                       'tamanio_letra': campo_tamanio_letra_form}},
            {'valor_x_variable': {'text': str(total_dias_disponible),
                                  'x_variable':130,
                                  'tipo_letra': valor_tipo_letra_form,
                                  'tamanio_letra': valor_tamanio_letra_form}},
        ]
        # resumen
        p.rect(x_resumen, y_resumen, ancho_resumen, alto_resumen)
        formulario(p, x_form_resumen, y_form_resumen, lista_form_resumen, switcher_formulario, switcher_salto_linea, switcher_padding_left)


        #Mostrar pagina y guardar los cambios
        p.showPage()
        p.save()
        return response

class DocenteList(generics.ListAPIView):
    serializer_class = DocenteSerializer
    queryset = Docente.objects.all().order_by('-id')

