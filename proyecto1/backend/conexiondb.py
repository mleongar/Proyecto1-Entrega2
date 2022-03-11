import pymysql

def obtener_conexion():
    return pymysql.connect(host='dbcloud.cglc0r2vyjzj.us-east-1.rds.amazonaws.com',
                                user='cloud',
                                password='uniandeS.1',
                                db='supervoices')
