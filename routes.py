from flask import Flask, request, jsonify, render_template
from models import db, Medicine
from preprocess import predict_quality
import os

def setup_routes(app):
    @app.route('/')
    def home():
        return render_template("index.html")

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        template_path = os.path.abspath("templates/upload.html")

        # Ensure upload.html exists
        if not os.path.exists(template_path):
            return jsonify({"error": "upload.html not found!"}), 404  

        if request.method == 'GET':
            return render_template("upload.html")

        # Get form data
        name = request.form.get('name')
        ingredients = request.form.get('ingredients')

        # Validate input
        if not name or not ingredients:
            return jsonify({"error": "Both 'name' and 'ingredients' are required!"}), 400  

        # Debugging info
        print(f"Received: Name={name}, Ingredients={ingredients}")

        # Predict quality
        try:
            quality = predict_quality(ingredients)
        except Exception as e:
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500  

        # Save to database
        try:
            new_medicine = Medicine(name=name, ingredients=ingredients, quality=quality)
            db.session.add(new_medicine)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500  

        return render_template("result.html", name=name, quality=quality)

    @app.route('/medicines', methods=['GET'])
    def get_medicines():
        medicines = Medicine.query.all()
        return jsonify([{'id': m.id, 'name': m.name, 'quality': m.quality} for m in medicines])
