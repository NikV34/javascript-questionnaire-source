from flask import Flask
from flask_cors import CORS
from flask import request
from flask import jsonify
import re
import urllib.request


app = Flask(__name__)
CORS(app)

app.config['ENV'] = 'development'


def get_html(url):
    try:
        response = urllib.request.urlopen(url)
        return response.read()
    except urllib.error.URLError:
        return False


def parse_page(content):
    content = content.decode('utf-8')
    k = re.finditer("(^#{6})(.|\n)+?(</details>$)", content, flags=re.MULTILINE)
    test_list = []
    counter = 0
    for i in k:
        counter += 1
        question = re.search("[^#{6} \d+. ](.+)", i.group(0))
        task = re.search("(```)((.|\n)+?)(```)", i.group(0))
        option_list = [ans.group(2) for ans in re.finditer("(-\s\w:\s)(.+$)", i.group(0), flags=re.MULTILINE)]
        answer = re.search("(^#{4} Answer: .)((.|\n)+?)(</p>)", i.group(0), flags=re.MULTILINE)
        test_list.append({
            "id": counter,
            "question": question.group(0) if question else "",
            "task": task.group(2).strip() if task else "",
            "option_list": option_list,
            "answer": (ord(answer.group(1)[-1].lower()) - 96) - 1,
            "explanation": answer.group(2).strip()
        })
    return test_list


@app.route('/', methods=['GET'])
def test():
    if request.method == 'GET':
        base_url = "https://raw.githubusercontent.com/lydiahallie/javascript-questions/master/README.md"
        content = get_html(base_url)
        if content:
            return jsonify(parse_page(content))
        else:
            return jsonify("no content")


if __name__ == '__main__':
    app.run()
