import platform

if platform.system() == "Darwin":  # Mac系统
    import pymysql

    pymysql.install_as_MySQLdb()
