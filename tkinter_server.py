from flask import Flask, request, json

app = Flask(__name__)

@app.route('/check_bbox_inside_image/', methods = ['POST'])
def check_bbox_inside_image():
    data = json.loads(request.data)
    print("This is the data I got : ", data)
    print("yea yeah")
    print("\n\n\n")

    return {"message" : "success", "status_code" : 200}

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,threaded=True,debug=False)