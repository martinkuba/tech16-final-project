from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import Chatbot

app = Flask(__name__)
CORS(app)  # This will allow all domains by default

chatbot = Chatbot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    # print(data)

    prompt = data.get('prompt', '')
    request_type = data.get('type', '')
    context = data.get('context', '')

    # print(prompt)
    # print(request_type)
    # print(context)

    if request_type == 'current-note':
        print("Asking LLM using a single-file context")
        response = chatbot.ask_with_context(prompt, context)
        return jsonify({'response': response['response'], 'sources': response['sources']})
    elif request_type == 'all-notes':
        print("Asking LLM using RAG context")
        response = chatbot.ask_with_rag(prompt)
        return jsonify({'response': response['response'], 'sources': response['sources']})
    elif request_type == 'find-files':
        print("Search for documents using RAG")
        response = chatbot.find_rag_document(prompt)
        return jsonify({'response': response})

    # print('****************')
    # print(response_text)
    # print(type(response_text))
    # print(vars(response_text))
    # print('****************')
    # return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(port=8181, debug=True)
