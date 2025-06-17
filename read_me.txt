Django admin & GAT admin
========================
user:	admin
name:	Administrator
phone:	99999999
passwd:	admin

GAT users
=========
phone:	99990000
passwd:	147258

Flow
====
- sign up (registration): phone, password
- login: phone, password
- gat_portal(user.is_admin_: define if system admin
  - if is_admin -> sysadmin_main.html
    else -> gat_app/user_main.html



Variables
=========
- session
  - uid = logged in user id
  - uname = logged in user name (UserProfile.name)
  - is_admin = True: system admin, False: general user


