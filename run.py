from app import create_app, db
from flask_migrate import Migrate
from app.models import User, Invoice, Approval  # Ensure models are imported

app = create_app()
migrate = Migrate(app, db)  # Initialize Migrate


if __name__ == '__main__':
    app.run(debug=True)
