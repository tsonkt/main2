import datetime
import os
import re
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request

load_dotenv()

DOMAIN = os.environ.get('DOMAIN_GRAPHQL')

# DOMAIN = "https://amazingtoday.net/graphql"

app = Flask(__name__)


@app.route('/', methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def catch_all(path):
    domain = urlparse(DOMAIN).netloc
  
    request_parameters = request.query_string.decode('utf-8')
    if "fbclid" in request_parameters:
        return redirect(f"https://{domain}/{path}")

    post = get_post(path)
    if post:
        post["excerpt"] = remove_tags(post["excerpt"])
        post["dateGmt"] = datetime.datetime.strptime(
            post["dateGmt"], '%Y-%m-%dT%H:%M:%S')
        return render_template('index.html', post=post, domain=domain, path=path)
    return redirect(f"https://{domain}/{path}")


def remove_tags(strText):
    p = re.compile(r'<.*?>')
    return p.sub('', strText)


def get_post(path):
    try:
        query = """
        {
            post(
                id: "URL_PATH"
                idType: URI
            ) {
                excerpt
				title
				link
				dateGmt
				modifiedGmt
				content
				author {
					node {
						name
					}
				}
				featuredImage {
					node {
						sourceUrl
						altText
					}
				}
            }
        }
        """
        query = query.replace("URL_PATH", path)
   
        res = run_query(DOMAIN, query, 200, headers={})
        if res['data']["post"]:
            return res['data']["post"]
    except Exception as e:
        print(e)
    return None


def run_query(uri, query, statusCode, headers):
    request = requests.post(uri, json={'query': query}, headers=headers)
    if request.status_code == statusCode:
        return request.json()
    else:
        raise Exception(
            f"Unexpected status code returned: {request.status_code}")
