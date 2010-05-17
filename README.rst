INTRODUCTION
============

MoneyDJ is an application to manage personal finances. It is written in Python
using Django as a framework. 


INSTALLING
==========

Prerequisites:
* Python (2.6 is the only version that has been tested, though 2.5 should work)
* A database module for python (e.g. python-mysqldb)
* Django (v1.2 or greater) installed in your distribution packages folder
  (see http://docs.djangoproject.com/en/dev/topics/install/)
* A web server (e.g. Apache or nginx)
* wsgi module (e.g. mod_wsgi for Apache or nginx)

1. Extract the files to a folder readable by your webserver (e.g.
   /var/www/moneydj-dist/) so that the /moneydj subfolder is contained within 
   this folder (i.e. /var/www/moneydj-dist/moneydj/ exists)
2. Edit moneydj/apache/moneydj.wsgi and replace /var/www/moneydj-dist/ with the 
   folder you extracted the files to
3. Create a virtualhost for the site (an example one is included in the same
   folder as this README file)
4. Edit moneydj/settings.py
    1. Edit the database section. If you are using PostgreSQL or MySQL then
       either use 'django.db.backends.postgresql_psycopg2' or
       'django.db.backends.mysql' as the backend and edit the database name,
       username and password information. If you wish to use SQLite, use
       'django.db.backends.sqlite3' as the ENGINE, the absolute path to the 
       SQLite database file as the NAME and remove the USER and PASSWORD fields
    2. If you wish to use a cache, uncomment either memcache (if you have it 
       installed) or the file cache line, and comment the dummy:// line

    3. Edit MEDIA_ROOT to point to the path you extracted the files to

    4. If you configured your media to be served on a different VHost or by a
       different browser, or you are not running the site on localhost, edit
       MEDIA_URL
5. Add /var/www/moneydj-dist/django/ to your site packages directory by running
   the following command: ::
    ln -s /var/www/moneydj-dist/django-trunk/django `python -c "from \
      distutils.sysconfig import get_python_lib; print get_python_lib()"`/django
6. Run the following command: ::
    python /var/www/moneydj-dist/moneydj/manage.py syncdb
   The script will ask you if you want to create a superuser. It is recommended
   that you do so you will have access to Django's admin interface (at /admin/)
7. Restart your web server and point your browser at http://localhost or the
   domain you have installed the site to
