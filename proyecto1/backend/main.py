from flask import Flask, render_template, request, redirect, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import administrador
import locutor
import concurso
import propuesta

app = Flask(__name__, static_folder= 'static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
"""
Definición de rutas    
"""

@app.route("/")
def index():
    concursos = concurso.obtener_concurso() 
    propuestasporlocutor = propuesta.obtener_Propuesta_por_concurso_por_locutor()
    return render_template("index.html", concursos = concursos, propuestasporlocutor = propuestasporlocutor)
    
@app.route("/sesion")
def sesion():
      return render_template("login.html")

@app.route("/administradores/<int:id>", methods=['GET'])
def administradores(id):
      concursos = concurso.obtener_concurso_admon(id) 
      propuestasporlocutor = propuesta.obtener_Propuesta_por_concurso_por_locutor_id(id)      
      return render_template("administrador.html", concursos = concursos, propuestasporlocutor = propuestasporlocutor, id =id)

@app.route("/propuestas/<int:id>", methods=['GET'])
def propuestas(id):
      return render_template("crearpropuesta.html", id = id)

@app.route("/crearcuenta")
def crearcuenta():
      return render_template("register.html")    
      
@app.route("/crearconcurso/<int:id>", methods=['GET'])
def crearconcurso(id):
      return render_template("crearconcurso.html", id = id)   
      
@app.route('/crearadministrador', methods=['POST'])
def crearadministrador():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    password = request.form["password"]
    password2 = request.form["password2"]
    if password == password2:
      admon = administrador.obtener_admon_por_email(email)
      if admon:
        print ('El correo ya existe')
        return render_template("login.html")
      administrador.insertar_admon(nombre, apellido, email, password)
      return render_template("login.html")
    print ('Las contraseñas son diferentes')
    return render_template("register.html")
    
@app.route("/login", methods=['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    admon = administrador.obtener_admon_por_email(email) 
    if not admon or not admon[4] == password:
      print ('Usuario o contrasena incorrecta')
      return render_template("login.html")
    return redirect(url_for("administradores", id = admon[0]))

@app.route("/verconcursoadmon/<int:id>", methods=['GET'])
def verconcursoadmon(id):
    concursos = concurso.obtener_concurso_admon(id) 
    if not concursos:
      return redirect(url_for("administradores", id = id))
    return render_template("modificarconcurso.html", concursos = concursos)

@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/crearconcurso2", methods=['GET','POST'])
def crearconcurso2():
    id_concurso = concurso.obtener_maxid()
    id_admon = request.form["id"]
    nombre = request.form["nombre"]
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    file = request.files["logo"]
    file.save(os.path.join("static/nfs/logos", dt_string+file.filename))
    logo = 'nfs/logos/'+dt_string+file.filename
    url = request.form["url"]
    valida = concurso.obtener_url(url) 
    if valida:
      print ('URL ya existe')
      return redirect(url_for("crearconcurso", id = id_admon))
    fecha_inicio = request.form["inicio"]
    fecha_fin = request.form["fin"]
    valor = request.form["valor"]
    guion = request.form["guion"]
    recomendacion = request.form["recomendacion"]
    concurso.insertar_concurso(nombre,id_admon,logo,url,fecha_inicio,fecha_fin,valor,guion,recomendacion)
    return redirect(url_for("administradores", id = id_admon))

@app.route('/editarconcurso/<int:id>', methods=['GET'])
def editarconcurso(id):
    concursos = concurso.obtener_concurso_por_id(id) 
    return render_template("editarconcurso.html", concursos = concursos)

@app.route('/editarconcurso2/<int:id>',  methods=['GET', 'POST'])
def editarconcurso2(id):
    concursos = concurso.obtener_concurso_por_id(id) 
    if request.method == 'POST':
      nombre = request.form['nombre']
      now = datetime.now()
      dt_string = now.strftime("%d%m%Y%H%M%S")
      file = request.files["logo"]
      file.save(os.path.join("static/nfs/logos", dt_string+file.filename))
      logo = 'nfs/logos/'+dt_string+file.filename
      url = request.form["url"]
      valida = concurso.obtener_url(url) 
      if valida:
        print ('URL ya existe')
        return redirect(url_for("editarconcurso", id = id))
      fecha_inicio = request.form['inicio']
      fecha_fin = request.form['fin']
      valor = request.form['valor']
      guion = request.form['guion']
      recomendacion = request.form['recomendacion']
      concurso.actualizar_concurso(id,nombre,logo,url,fecha_inicio,fecha_fin,valor,guion,recomendacion)
    return redirect(url_for("verconcursoadmon", id = concursos[2]))

@app.route('/eliminarconcurso/<int:id>', methods=['GET'])
def eliminarconcurso(id):
    propuesta.eliminar_Propuesta_concurso(id)
    admon = concurso.obtener_concurso_por_id(id)
    concursos = concurso.eliminar_concurso(id)
    return redirect(url_for("verconcursoadmon", id = admon[2]))
    
@app.route("/crearlocutor")
def crearlocutor():
    return render_template("index.html")
    
@app.route("/crearpropuesta/<int:id>",methods=['GET','POST'])
def crearpropuesta(id):
    print (id)
    return render_template("crearpropuesta.html", id =id)
# post para subir el audio

@app.route("/subirpropuesta",methods=['GET','POST'])
def subirpropuesta():
  #verificación de locutor por email
    ruta_audio = "static/nfs/audios_originales/"
    email = request.form["email"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    mensaje = request.form["observacion"]
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S%f")
    loc = locutor.obtener_locutor_por_email(email)
    if loc:
        id_loc = loc
    else:
        locutor.insertar_locutor(nombre,apellido,email)  
        loc =  locutor.obtener_locutor_por_email(email)
        id_loc = loc
    fecha = request.form["fecha"]
    id_concurso = request.form["id_concurso_oculto"]
    estado = "En proceso"
    file = request.files["file"]
    file.save(os.path.join("static/nfs/audios_originales/", dt_string+file.filename))
    voz_original = ruta_audio + dt_string + file.filename
    voz_convertida = ""
    propuesta.insertar_Propuesta(fecha,loc,id_concurso,estado,voz_original,voz_convertida,mensaje)
    return render_template("resultadopropuesta.html",message="Hemos recibido tu voz y la estamos procesando para que sea publicada en la página del concurso y pueda ser posteriormente revisada por nuestro equipo de trabajo. Tan pronto la voz quede publicada en la página del concurso te notificaremos por email.")

@app.route("/convertirvoz")
def convertirvoz():
    return render_template("index.html")
    
@app.route("/modificarpropuesta")
def modificarpropuesta():
    return render_template("index.html")
    
@app.route("/enviarcorreo")
def enviarcorreo():
    return render_template("index.html")

@app.route("/detalleconcurso/<string:id>", methods=['GET'])
def detalleconcurso(id):
    Concurso = concurso.obtener_url(id) 
    con_par = propuesta.obtener_Propuesta_por_concurso(Concurso[0])
    if not con_par:
        print ('No hay participantes')
        return render_template("detalleconcurso.html", con_par = con_par,  Concurso=Concurso)
    return render_template("detalleconcurso.html", con_par = con_par,  Concurso=Concurso)

@app.route("/detallarconcurso/<string:id>", methods=['GET'])
def detallarconcurso(id):
    Concurso = concurso.obtener_url(id) 
    con_par = propuesta.obtener_Propuesta_por_concurso(Concurso[0])
    return render_template("detallarconcurso.html", con_par = con_par, id = Concurso[0], Concurso=Concurso)

# Iniciar el servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
