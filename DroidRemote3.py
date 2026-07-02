from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import os
import re
import paramiko
import socket

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# User authentication
USERS = {}
try:
    with open("users.txt", "r") as f:
        for line in f:
            username, password = line.strip().split(":")
            USERS[username] = password
except FileNotFoundError:
    pass

# Configuration
DEVICE_IP = "192.168.1.100"  # Will be dynamically updated
ADB_PORT = "5555"
FRIDA_PORT = "27042"
SCRCPY_PORT = "1234"
SCRCPY_BINARY = "/usr/bin/scrcpy"  # Adjust if needed

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" in session:
        if request.method == "POST":
            if "start" in request.form:
                try:
                    subprocess.run(["adb", "connect", f"{DEVICE_IP}:{ADB_PORT}"], check=True)
                    subprocess.Popen(["adb", "shell", "frida-server &"])
                    subprocess.Popen([SCRCPY_BINARY, "-s", f"{DEVICE_IP}:{SCRCPY_PORT}"])
                    subprocess.Popen(["adb", "shell", "frida-trace -U -l /data/local/tmp/frida_hook.js &"])
                    return redirect(url_for("index"))
                except Exception as e:
                    return f"Error: {e}"

            elif "stop" in request.form:
                try:
                    subprocess.run(["adb", "disconnect"])
                    subprocess.run(["adb", "shell", "killall frida-server"])
                    subprocess.run(["pkill", "scrcpy"])
                    return redirect(url_for("index"))
                except Exception as e:
                    return f"Error: {e}"

            elif "file_transfer" in request.form:
                file = request.files.get("file")
                if file:
                    file.save(f"/data/local/tmp/{file.filename}")
                    return "File uploaded!"

            elif "file_explorer" in request.form:
                return redirect(url_for("file_explorer"))

            elif "mic_capture" in request.form:
                return redirect(url_for("mic_capture"))

            elif "speak" in request.form:
                return redirect(url_for("speak"))

            elif "qr_code" in request.form:
                return redirect(url_for("qr_code"))

            elif "notification" in request.form:
                message = request.form.get("message")
                if message:
                    subprocess.run(["adb", "shell", "am start -a android.intent.action.SEND -d 'text/plain' --es 'android.intent.extra.TEXT' '{}'.format(message)"])
                return redirect(url_for("index"))

            elif "media_send" in request.form:
                file = request.files.get("media")
                if file:
                    file.save(f"/data/local/tmp/{file.filename}")
                    subprocess.run(["adb", "push", f"/data/local/tmp/{file.filename}", "/sdcard/Download/"])
                    return "Media uploaded!"

        return render_template("index.html", username=session["username"])
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return "Invalid username or password"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/ssh")
def ssh():
    return render_template("ssh.html")

@app.route("/ssh", methods=["POST"])
def ssh_post():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("your_device_ip", username="root", password="your_password")
    stdin, stdout, stderr = ssh.exec_command("ls")
    output = stdout.read().decode()
    error = stderr.read().decode()
    ssh.close()
    return f"Output: {output}\nError: {error}"

@app.route("/file_explorer")
def file_explorer():
    return render_template("file_explorer.html")

@app.route("/mic_capture")
def mic_capture():
    return render_template("mic_capture.html")

@app.route("/speak")
def speak():
    return render_template("speak.html")

@app.route("/qr_code")
def qr_code():
    return render_template("qr_code.html")

@app.route("/notification")
def notification():
    return render_template("notification.html")

@app.route("/media_send")
def media_send():
    return render_template("media_send.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
