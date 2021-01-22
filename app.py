import os
from flask import Flask, jsonify, render_template, request, flash, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from formsLogin import FormLog, FormForgot
import yagmail
import utils
import conexion
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.urandom(23)

PEOPLE_FOLDER = os.path.join('static', 'upload')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
ALLEXTENDS = set(["png", "jpg", "jpge", "gif"])
app.secret_key = os.urandom(23)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLEXTENDS


@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
@app.route('/login/<string:titulo>', methods=['GET', 'POST'])
@app.route('/login/<string:titulo>/<string:mensaje>', methods=['GET', 'POST'])
def login(titulo=None, mensaje=None):  # esto sirve para unir las páginas
    formlog = FormLog()
    titulo = "Autenticarse"
    if request.method == 'GET':
        return render_template('Login.html', formlog=formlog, titulo=titulo)
    try:
        if request.method == 'POST':
            email = request.form['usuario']  # sacar los campos del form
            password = request.form['password']
            if utils.isEmailValid(email):
                if utils.isPasswordValid(password):
                    rol = sqlLogin(email, password)
                    if not rol is None:
                        rol = list(rol)
                        if rol[0] == 1:
                            session['username'] = rol[1]
                            return render_template("portalAdmin.html", formlog=formlog, titulo=titulo)
                        elif rol[0] == 2:
                            session['username'] = rol[1]
                            mensaje = "Mintic-Sports"
                            return render_template('index.html', titulo=mensaje)
                    else:
                        mensaje = 'Credenciales incorrectas'
                        return render_template("Login.html", formlog=formlog, mensaje=mensaje)
                else:
                    mensaje = "Porfavor ingrese una contraseña válida"
                    return render_template("Login.html", formlog=formlog, titulo=titulo, mensaje=mensaje)
            else:
                mensaje = "ingrese un usuario válido"
                return render_template("Login.html", formlog=formlog, titulo=titulo, mensaje=mensaje)
        else:
            return render_template('Login.html', formlog=formlog, titulo=titulo)
    except:
        return render_template('Login.html', formlog=formlog, titulo=titulo)


@app.route('/cerrarsesion', methods=['GET'])
def cerrarSesion():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/portalAdmin/<string:mensaje>', methods=['GET', 'POST'])
@app.route('/portalAdmin', methods=['GET', 'POST'])
def portalA(mensaje=None):  # esto sirve para unir las páginas
    mensaje = "PortalAdmin"
    if 'username' in session:
        username = session['username']
        return render_template('portalAdmin.html', titulo=mensaje, user=username)
    else:
        return redirect(url_for('login'))


@app.route('/modificacion/<string:mensaje>', methods=['GET', 'POST'])
@app.route('/modificacion', methods=['GET', 'POST'])
def mod(mensaje=None):  # esto sirve para unir las páginas
    titulo = "Administración de Stock"
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            try:

                # sacar los campos del form
                fullName = request.form['fullName']
                empCode = request.form['empCode']
                precio = request.form['precio']
                cantidad = request.form['cantidad']
                categoria = request.form['categoria']
                f = request.files["getimage"]

                if allowed_file(f.filename):

                    now = datetime.now()
                    filename = secure_filename(str(now)+str(f.filename))
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    mensaje = sqlNewProduct(fullName, int(
                        cantidad), now, empCode, filename, int(precio), categoria)
                    return redirect(url_for('mod'))
                else:
                    mensaje = "extencion no valida"
                    return render_template('tablaAdmin.html', titulo=titulo, mensaje=mensaje)
            except:

                return render_template('tablaAdmin.html', titulo=titulo)
        else:
            productos = sqlListProduct()
            return render_template('tablaAdmin.html', titulo=titulo, productos=productos)
    else:
        return redirect(url_for('login'))

# sqlBuscarProduct(id)


@app.route('/editarproducto/<string:id>', methods=['GET', 'POST'])
@app.route('/editarproducto', methods=['GET', 'POST'])
def modificarProducto(id=None):
    titulo = "Administración de Stock"
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            try:
                # sacar los campos del form
                fullName = request.form['fullName']
                empCode = request.form['empCode']
                precio = request.form['precio']
                cantidad = request.form['cantidad']
                iduser = request.form['id']
                f = request.files['getimage']
                img = request.form['img']
                categoria = request.form['categoria']
                iduser = iduser.rsplit('=', 1)[1]

                if img == "":
                    if allowed_file(f.filename):
                        now = datetime.now()
                        filename = secure_filename(str(now)+str(f.filename))
                        f.save(os.path.join(
                            app.config['UPLOAD_FOLDER'], filename))
                        mensaje = sqlUpdateProduct2(fullName, int(
                            cantidad), empCode, filename, int(precio), categoria, int(iduser))
                        return redirect(url_for('mod'))

                if allowed_file(f.filename):
                    now = datetime.now()
                    filename = secure_filename(str(now)+str(f.filename))
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                    mensaje = sqlUpdateProduct2(fullName, int(
                        cantidad), empCode, filename, int(precio), categoria, int(iduser))
                    return redirect(url_for('mod'))
                else:
                    mensaje = sqlUpdateProduct(fullName, int(
                        cantidad), empCode, int(precio), categoria, int(iduser))
                    return redirect(url_for('mod'))

            except:
                return redirect(url_for('mod'))
        else:
            productoB = sqlBuscarProduct(id)
            return render_template('tablaAdmin.html', titulo=titulo, productoB=productoB, id=id)
    else:
        return redirect(url_for('login'))


@app.route('/registroUsuarios/<string:mensaje>', methods=['GET', 'POST'])
@app.route('/registroUsuarios', methods=['GET', 'POST'])
def registroU(mensaje=None):  # esto sirve para unir las páginas
    mensaje = "Registro Usuarios"
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            try:
                nombre = request.form['nombre']  # sacar los campos del form
                password = request.form['password']
                password2 = request.form['password2']
                if password == password2:
                    email = request.form['email']
                    if utils.isEmailValid(email):
                        if utils.isUsernameValid(nombre):
                            if utils.isPasswordValid(password):
                                fecha = datetime.now()
                                mensaje2 = sqlNewUsuario(
                                    nombre, password, email, fecha)
                                return render_template('Registrarse.html', titulo=mensaje, mensaje2=mensaje2)
                            else:
                                mensaje2 = "password no valida"
                                return render_template('Registrarse.html', titulo=mensaje, mensaje2=mensaje2)
                        else:
                            mensaje2 = "Nombre no valido"
                            return render_template('Registrarse.html', titulo=mensaje, mensaje2=mensaje2)
                    else:
                        mensaje2 = "Email no valido"
                        return render_template('Registrarse.html', titulo=mensaje, mensaje2=mensaje2)
                else:
                    mensaje2 = "Las contraseñas nos coinciden"
                    return render_template('Registrarse.html', titulo=mensaje, mensaje2=mensaje2)
            except:
                return render_template('Registrarse.html', titulo=mensaje)
        else:
            return render_template('Registrarse.html', titulo=mensaje)
    else:
        return redirect(url_for('login'))


@app.route('/recuperarContrasena', methods=['GET', 'POST'])
@app.route('/recuperarContrasena/<string:titulo>', methods=['GET', 'POST'])
@app.route('/recuperarContrasena/<string:titulo>/<string:mensaje>', methods=['GET', 'POST'])
# esto sirve para unir las páginas
def recuperarContraseña(titulo=None, mensaje=None):
    titulo = "Forgot password"
    formforg = FormForgot()
    if request.method == 'GET':
        return render_template('Recu_contrasena.html', formforg=formforg, titulo=titulo)

    try:
        if request.method == 'POST':
            email = request.form['email']  # sacar los campos del form
            if utils.isEmailValid(email):
                email = sqlforgot(email)
                if not email is None:
                    email = list(email)
                    yag = yagmail.SMTP('uninorte@uninorte.edu.co', 'clave')
                    yag.send(to=email, subject='validar cuenta',
                             contents='Bienvenido usa este link para activar tu cuenta')
                    mensaje = 'revisa tu correo: ' + \
                        str(email)+', al cual se le han eviado las credenciales'
                    return render_template('Recu_contrasena.html', formforg=formforg, titulo=titulo)
                else:
                    mensaje = 'Email no existe en la base de datos'
                    return render_template('Recu_contrasena.html', formforg=formforg, titulo=titulo, mensaje=mensaje)
            else:
                mensaje = 'Email no es valido'
                return render_template('Recu_contrasena.html', formforg=formforg, titulo=titulo, mensaje=mensaje)
        else:
            return render_template('Recu_contrasena.html', formforg=formforg, titulo=titulo)

    except:
        return render_template('Recu_contrasena.html', formforg=formforg, titulo=titulo)


@app.route('/eliminarProducto/<string:id>', methods=['GET', 'POST'])
@app.route('/eliminarProducto/<string:id>/<string:img>', methods=['GET', 'POST'])
@app.route('/eliminarProducto/<string:id>/<string:img>/<string:categoria>', methods=['GET', 'POST'])
@app.route('/eliminarProducto', methods=['GET', 'POST'])
def eliminarProducto(id=None, img=None, categoria=None):
    if 'username' in session:
        sqlEliminarProduct(id)
        img = img.rsplit('=', 1)[1]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
        username = session['username']
        if username == "admin":
            return redirect(url_for('mod'))
        else:
            titulo = "Mintic-Sports"
            categoria = categoria.rsplit('=', 1)[1]
            data = sqlBuscarProductcategoria(categoria)
            if data == "" or data is None or len(data) <= 0:
                mensaje = "No hay datos en esta categoria"
                return render_template('index.html', titulo=titulo, mensaje=mensaje)
            else:
                return render_template('Vista5.html', titulo=titulo, data=data)
    else:
        return redirect(url_for('login'))


@app.route('/listarusuarios', methods=['GET'])
@app.route('/listarusuarios/<string:id>', methods=['GET'])
def listarusuarios(id=None):
    if 'username' in session:
        titulo = "Listar usuarios"
        users = sqllistUser()
        return render_template('listarUsuarios.html', titulo=titulo, user=users)
    else:
        return redirect(url_for('login'))


@app.route('/index/<string:mensaje>', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(mensaje=None):
    mensaje = "Mintic-Sports"
    if 'username' in session:
        username = session['username']
        return render_template('index.html', titulo=mensaje)
    else:
        return redirect(url_for('login'))


@app.route('/categoria/<string:categoria>', methods=['GET', 'POST'])
@app.route('/categoria', methods=['GET', 'POST'])
def CATEGORIA(categoria=None):
    titulo = "Mintic-Sports"

    if 'username' in session:

        username = session['username']
        if request.method == 'POST':
            cantidad = request.form['cantidad']  # sacar los campos del form
            idu = request.form['id']  # sacar los campos del form
            categoria = request.form['categoria']  # sacar los campos del form
            mensaje = sqlupdateProduct(int(cantidad), int(idu))

            data = sqlBuscarProductcategoria(categoria)
            return render_template('Vista5.html', titulo=titulo, mensaje=mensaje, data=data)
        else:

            categoria = categoria.rsplit('=', 1)[1]
            if str(categoria) == 'Camisa':
                mensaje = "Actualizar"+categoria
                data = sqlBuscarProductcategoria(categoria)

                if data == "" or data is None or len(data) <= 0:
                    return render_template('Vista5.html', titulo=mensaje, data=data)
                else:
                    return render_template('Vista5.html', titulo=mensaje, data=data)
            elif str(categoria) == 'Deportiva':
                mensaje = "Actualizar"+categoria
                data = sqlBuscarProductcategoria(categoria)

                if data == "" or data is None:
                    return render_template('index.html', titulo=mensaje)
                else:
                    return render_template('Vista5.html', titulo=mensaje, data=data)
            elif str(categoria) == 'Zapatos':
                mensaje = "Actualizar"+categoria
                data = sqlBuscarProductcategoria(categoria)

                if data == "" or data is None:
                    return render_template('index.html', titulo=mensaje)
                else:
                    return render_template('Vista5.html', titulo=mensaje, data=data)

        return render_template('index.html', titulo=mensaje)
    else:
        return redirect(url_for('login'))


@app.route('/buscar/<string:mensaje>', methods=['GET', 'POST'])
@app.route('/buscar', methods=['GET', 'POST'])
def Buscar(mensaje=None):
    titulo = "Buscar"
    if 'username' in session:
        username = session['username']
        try:
            if request.method == 'POST':

                buscar = request.form['buscar']  # sacar los campos del form
                producto = sqlBuscarProductLike(buscar)
                if producto == "" or producto is None or len(producto) <= 0:
                    mensaje = "NO hay producto con el criterio de busqueda "+buscar
                    return render_template('buscar.html', titulo=titulo, mensaje=mensaje)
                else:
                    return render_template('buscar.html', titulo=titulo, producto=producto)
            else:
                return render_template('buscar.html', titulo=titulo)
        except:

            return render_template('buscar.html', titulo=mensaje, mensaje="ocurrio un error")

    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)


# ===================
#      SQL - Admin
# ===================


# =====================
#   SQL - LOGIN
# =====================
def sqlLogin(email, password):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT rol,username from users WHERE email='" + \
        email+"' AND password='"+password+"';"
    cur.execute(sql)
    rol = cur.fetchone()
    conex.close()
    return rol


def sqlforgot(email):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT email from users WHERE email='"+email+"';"
    cur.execute(sql)
    email = cur.fetchone()
    conex.close()
    return email


def sqllistUser():
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT * from users WHERE rol=2"
    cur.execute(sql)
    users = cur.fetchall()
    conex.close()
    return users

# =====================
#   SQL - Producto
# =====================


def sqlNewProduct(fullName, cantidad, now, empCode, filename, precio, categoria):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "INSERT INTO productos (nombre,cantidad,creatad,referencia_cog,img,precio,categoria) VALUES('%s','%d','%s','%s','%s','%d','%s')" % (
        fullName, cantidad, now, empCode, filename, precio, categoria)
    cur.execute(sql)
    conex.commit()
    conex.close()
    return "Producto agregado..."


def sqlListProduct():
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT * FROM productos"
    cur.execute(sql)
    productos = cur.fetchall()
    conex.close()
    return productos


def sqlUpdateProduct(fullName, cantidad, empCode, precio, categoria, id):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "update productos set nombre = '%s', cantidad = '%d', referencia_cog='%s',precio='%d',categoria='%s' where id = '%d';" % (
        fullName, cantidad, empCode, precio, categoria, id)
    cur.executescript(sql)
    conex.close()
    return "Datos actualizados....."


def sqlUpdateProduct2(fullName, cantidad, empCode, filename, precio, categoria, id):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "update productos set nombre = '%s', cantidad = '%d', referencia_cog='%s',img='%s',precio='%d', categoria='%s'where id = '%d';" % (
        fullName, cantidad, empCode, filename, precio, categoria, id)
    cur.executescript(sql)
    conex.close()
    return "Datos actualizados....."


def sqlEliminarProduct(id):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "DELETE from productos WHERE "+id
    cur.executescript(sql)
    conex.close()
    return "Registro eliminado..."

# =====================
#   SQL- Cajero
# =====================


def sqlNewUsuario(nombre, password, email, fecha):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "INSERT INTO users (username,password,email,creatusers,rol) VALUES('%s','%s','%s','%s','%d')" % (
        nombre, password, email, fecha, 2)
    cur.execute(sql)
    conex.commit()
    conex.close()
    return "Usuario agregado exitosamente..."


def sqlBuscarProduct(id):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT * FROM productos WHERE "+id
    cur.execute(sql)
    product = cur.fetchone()
    conex.close()
    return product


def sqlBuscarProductcategoria(categoria):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT * FROM productos WHERE categoria='"+categoria+"'"
    cur.execute(sql)
    product = cur.fetchall()
    conex.close()
    return product


def sqlupdateProduct(cantidad, idu):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "UPDATE productos SET cantidad='%d' WHERE id='%d'" % (cantidad, idu)
    cur.execute(sql)
    conex.commit()
    conex.close()
    return "Producto actualizado..."


def sqlBuscarProductLike(buscar):
    conex = conexion.get_db()
    cur = conex.cursor()
    sql = "SELECT * FROM productos WHERE nombre like '%"+buscar+"%';"
    cur.execute(sql)
    product = cur.fetchall()
    conex.close()
    return product
