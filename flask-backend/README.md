# Flask RESTful API with MVC Architecture

This project is a Flask-based RESTful API that follows the Model-View-Controller (MVC) architecture. It serves as the backend for a web application, with a focus on clean code organization and separation of concerns.

## Project Structure

```
flask-backend
├── app
│   ├── __init__.py          # Initializes the Flask application
│   ├── controllers           # Contains controller classes for handling requests
│   │   └── example_controller.py
│   ├── models                # Contains model classes for data representation
│   │   └── example_model.py
│   ├── routes                # Defines API endpoints and links to controllers
│   │   └── example_routes.py
│   └── templates             # HTML templates for rendering views
│       └── base.html
├── tests                     # Unit tests for the application
│   └── test_example.py
├── requirements.txt          # Lists project dependencies
├── config.py                 # Configuration settings for the application
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd flask-backend
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```
   flask run
   ```

## Usage

Once the application is running, you can access the API endpoints defined in the `example_routes.py` file. Use tools like Postman or curl to test the endpoints.

## Testing

To run the unit tests, ensure your virtual environment is activated and execute:
```
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.