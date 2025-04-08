from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import yaml

app = Flask(__name__)

# Mock database
produtos = [
    {"id": 1, "nome": "Notebook", "preco": 3500.00, "estoque": 10},
    {"id": 2, "nome": "Mouse", "preco": 120.50, "estoque": 50}
]

# Swagger configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "API de Produtos"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/static/swagger.yaml')
def swagger():
    with open('templates/swagger.yaml', 'r') as f:
        return yaml.safe_load(f)

# CRUD Endpoints
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    """
    Lista todos os produtos
    ---
    tags:
      - Produtos
    responses:
      200:
        description: Lista de produtos
        schema:
          type: array
          items:
            $ref: '#/definitions/Produto'
    """
    return jsonify(produtos)

@app.route('/produtos/<int:id>', methods=['GET'])
def obter_produto(id):
    """
    Obtém um produto específico
    ---
    tags:
      - Produtos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do produto
    responses:
      200:
        description: Produto encontrado
        schema:
          $ref: '#/definitions/Produto'
      404:
        description: Produto não encontrado
    """
    produto = next((p for p in produtos if p['id'] == id), None)
    if produto:
        return jsonify(produto)
    return jsonify({"mensagem": "Produto não encontrado"}), 404

@app.route('/produtos', methods=['POST'])
def criar_produto():
    """
    Cria um novo produto
    ---
    tags:
      - Produtos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ProdutoInput'
    responses:
      201:
        description: Produto criado com sucesso
        schema:
          $ref: '#/definitions/Produto'
      400:
        description: Dados inválidos
    """
    novo_produto = request.get_json()
    if not novo_produto or 'nome' not in novo_produto or 'preco' not in novo_produto:
        return jsonify({"mensagem": "Dados inválidos"}), 400
    
    novo_id = max(p['id'] for p in produtos) + 1 if produtos else 1
    novo_produto['id'] = novo_id
    produtos.append(novo_produto)
    return jsonify(novo_produto), 201

@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    """
    Atualiza um produto existente
    ---
    tags:
      - Produtos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do produto
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ProdutoInput'
    responses:
      200:
        description: Produto atualizado
        schema:
          $ref: '#/definitions/Produto'
      404:
        description: Produto não encontrado
      400:
        description: Dados inválidos
    """
    produto = next((p for p in produtos if p['id'] == id), None)
    if not produto:
        return jsonify({"mensagem": "Produto não encontrado"}), 404
    
    dados = request.get_json()
    if not dados:
        return jsonify({"mensagem": "Dados inválidos"}), 400
    
    produto.update(dados)
    return jsonify(produto)

@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    """
    Remove um produto
    ---
    tags:
      - Produtos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do produto
    responses:
      200:
        description: Produto removido
      404:
        description: Produto não encontrado
    """
    global produtos
    produto = next((p for p in produtos if p['id'] == id), None)
    if not produto:
        return jsonify({"mensagem": "Produto não encontrado"}), 404
    
    produtos = [p for p in produtos if p['id'] != id]
    return jsonify({"mensagem": "Produto removido com sucesso"}), 200

if __name__ == '__main__':
    app.run(debug=True)
