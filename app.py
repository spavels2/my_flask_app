from flask import Flask, render_template, request, redirect, url_for
from forms import ImageForm
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)
app.config['SECRET_KEY'] = '6Ld3MqwqAAAAAGv8tmSfd7Hgwa1oQg_Q2awU5Gut'

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()
    if form.validate_on_submit():
        # Проверка_капчи
        recaptcha_response = request.form['g-recaptcha-response']
        payload = {
            'secret': app.config['SECRET_KEY'],
            'response': recaptcha_response
        }
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
        result = response.json()

         if not result.get('success'):
            return render_template('index.html', form=form, error='Проверка на робота не пройдена.')
            
        # Обработка изображения
        image_file = form.image.data
        stripe_width = form.stripe_width.data
        orientation = form.orientation.data

        # Сохранение изображения
        image_path = os.path.join('static', image_file.filename)
        image_file.save(image_path)

        # Изменение изображения
        modified_image_path = modify_image(image_path, stripe_width, orientation)

        return redirect(url_for('result', image_path=modified_image_path))
    return render_template('index.html', form=form)

@app.route('/result')
def result():
    image_path = request.args.get('image_path')
    return render_template('result.html', image_path=image_path)

@app.route('/modify', methods=['POST'])
def modify_image():
    image_file = request.files['image']
    stripe_width = int(request.form['stripe_width'])
    orientation = request.form['orientation']

    # Сохранение исходного изображения
    image_path = os.path.join('static', 'original_image.png')
    image_file.save(image_path)

    img = Image.open(image_path)
    img_array = np.array(img)

    # Изменение изображения
    if orientation == 'horizontal':
        for i in range(0, img_array.shape[0], stripe_width * 2):
            if i + stripe_width * 2 <= img_array.shape[0]:  # Проверка на выход за пределы
                # Обмен местами двух полос
                temp = img_array[i:i + stripe_width].copy()
                img_array[i:i + stripe_width] = img_array[i + stripe_width:i + stripe_width * 2].copy()
                img_array[i + stripe_width:i + stripe_width * 2] = temp
    else:
        for i in range(0, img_array.shape[1], stripe_width * 2):
            if i + stripe_width * 2 <= img_array.shape[1]:  # Проверка на выход за пределы
                # Обмен местами двух полос
                temp = img_array[:, i:i + stripe_width].copy()
                img_array[:, i:i + stripe_width] = img_array[:, i + stripe_width:i + stripe_width * 2].copy()
                img_array[:, i + stripe_width:i + stripe_width * 2] = temp

    modified_image = Image.fromarray(img_array)
    modified_image_path = os.path.join('static', 'modified_image.png')
    modified_image.save(modified_image_path)

    # Построение графика распределения цветов
    color_distribution = img_array.reshape(-1, img_array.shape[2])
    plt.figure(figsize=(10, 5))
    plt.hist(color_distribution, bins=256, color=['red', 'green', 'blue'], alpha=0.5, label=['Красный', 'Зеленый', 'Синий'])
    plt.title('Распределение цветов')
    plt.xlabel('Значение цвета')
    plt.ylabel('Частота')
    plt.legend()
    plt.savefig(os.path.join('static', 'color_distribution.png'))
    plt.close()

    return redirect(url_for('result', image_path=modified_image_path))
    
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    app.run(debug=True)

