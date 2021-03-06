from pro.user import user
from flask import request,render_template,redirect,jsonify,session
from pro import decorator
from pro import models,utils
import time


@user.route("/login",methods=["GET","POST"])
def login():
    msg = {}
    if request.method == "GET":
        return render_template("user/login.html")
    elif request.method == "POST":
        params = request.form
        userName = params.get("userName")
        passWord = params.get("passWord")
        user = models.db.session.query(models.StUser).filter(models.StUser.login_name==userName,models.StUser.delete_flag==0).first()
        if user is None:
            msg["code"] = 1001
            msg["msg"] = "账号或密码错误！"
        else:
            if user.login_name == userName and user.password == passWord:
                session["login_name"] = user.login_name
                session["userId"] = user.id
                session["avatar"] = user.avatar
                session["nickname"] = user.nickname
                session["password"] = user.password
                msg["code"] = 0
                msg["data"] = []
                msg["data"].append({"avatar":user.avatar,"nickname":user.nickname,"login_name":user.login_name})
                msg["msg"] = "登录成功！"
            else:
                msg["code"] = 1001
                msg["msg"] = "账号或密码错误！"
        return jsonify(msg)


@user.route("/logout")
def logout():
    session.clear()
    return redirect("/user/login")


@user.route("/getUserInfo")
@decorator.authentication
def getUserInfo():
    loginName = session.get("login_name")
    user = models.db.session.query(models.StUser).filter(models.StUser.login_name==loginName,models.StUser.delete_flag==0).first()
    if user is None:
        return render_template("404.html")
    else:
        return render_template("user/userInfo.html",content=user)


@user.route("/updatePassword",methods=["GET","POST"],endpoint="updatePassword")
@decorator.authentication
def updatePassword():
    msg = {}
    if request.method == "GET":
        return render_template("/user/updatePassword.html")
    loginName = session.get("login_name")
    params = request.form
    newPwd = params.get("password")
    user = utils.getUserByLoginName(loginName=loginName)
    if user:
        user.password = newPwd
        models.db.session.commit()
        msg["code"] = 0
        msg["msg"] = "请求成功！"
    else:
        msg["code"] = 1001
        msg["msg"] = "请求异常！"
    return jsonify(msg)


@user.route("/personalCenter",methods=["GET","POST"],endpoint="personalCenter")
@decorator.authentication
def personalCenter():
    msg = {}
    msg["data"] = []
    loginName = session.get("login_name")
    user = utils.getUserByLoginName(loginName=loginName)
    if request.method == "GET":
        categoryList = utils.getCategoryByuserId(userId=user.id)
        for categoryInfo in categoryList:
            categoryId = categoryInfo.id
            categoryName = categoryInfo.category_name
            categoryDes = categoryInfo.category_des
            categoryImg = categoryInfo.category_img
            contentList = utils.getContentByCategoryId(categoryId=categoryId)
            appendInfo = {
                "categoryId": categoryId,
                "categoryName": categoryName,
                "categoryDes": categoryDes,
                "categoryImg": categoryImg,
                "contentList": []
            }
            for contentInfo in contentList:
                contentId = contentInfo.id
                contentName = contentInfo.title
                appendInfo["contentList"].insert(0,{"contentId": contentId, "contentName": contentName})
            msg["data"].append(appendInfo)
        return render_template("user/personalCenter.html",content=msg)
    elif request.method == "POST":
        params = request.form
        msg["code"] = 0
        msg["msg"] = "请求成功！"
        return jsonify(msg)


@user.route("/addCategory",methods=["GET","POST"],endpoint="addCategory")
@decorator.authentication
def addCategory():
    if request.method == "GET":
        return render_template("user/addCategory.html")
    else:
        msg = {}
        msg["data"] = []
        params = request.form
        userId = session.get("userId")
        categoryName = params.get("categoryName")
        categoryDes = params.get("categoryDes")
        categoryImg = params.get("categoryImg")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        newCategory = models.StContentCategory(category_name=categoryName,category_des=categoryDes,category_img=categoryImg,user_id=userId,create_time=now,update_time=now)
        models.db.session.add(newCategory)
        models.db.session.commit()
        msg["msg"] = "请求成功！"
        msg["code"] = 0
        return jsonify(msg)


@user.route("/addComment",methods=["GET","POST"],endpoint="addComment")
@decorator.authentication
def addComment():
    msg = {}
    msg["data"] = []
    if request.method == "GET":
        params = request.args
        contentId = params.get("contentId")
        content = {
            "contentId":contentId
        }
        return render_template("user/addComment.html",content=content)
    else:
        params = request.form
        contentId = params.get("contentId")
        comment = params.get("comment")
        userId = session.get("userId")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        if contentId and comment and userId:
            newComment = models.StComment(user_id=userId,content_id=contentId,comment=comment,create_time=now,update_time=now)
            models.db.session.add(newComment)
            models.db.session.commit()
            msg["code"] = 0
            msg["msg"] = "保存成功！"
        else:
            msg["code"] = 1001
            msg["msg"] = "参数有误！"
        return jsonify(msg)