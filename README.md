# Youth Creativity and Expression Hub
The Youth Creativity and Expression Hub is a digital platform designed to empower young individuals by providing a space to explore, showcase, and develop their creative talents. Users can share their work and connect with mentors.

## Features
### Core Functionalities
- **User Profiles:**
Create personalized profiles with bio, areas of interest, and role (e.g., user or mentor).

- **Content Sharing:**
Upload and showcase creative works in categories like art, music, writing, and more.

- **Mentorship:**
Connect with mentors, schedule mentorship sessions, and receive guidance on creative projects.

- **Direct Messaging:**
Communicate with peers and mentors through a secure messaging system.

## Installation
### Prerequisites
authlib ~= 1.2
django ~= 4.2
python-dotenv ~= 1.0
requests ~= 2.31
daphne ~= 4.1 

### Setup Instructions
1. Clone the Repository:

```sh
git clone https://github.com/NadiaTeta/YouthTalent.git
```

2. Create a Virtual Environment:

```sh
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. Install Dependencies:

```sh
pip install -r requirements.txt
```

4. Set Up the Database:

Configure the database settings in settings.py.
Run migrations:

```sh
python manage.py migrate
```

5. Run the Development Server:

```
python manage.py runserver
```

6. Access the Application:
Open your browser and navigate to http://localhost:8000.

## Folder Structure
```sh
youth-creativity-hub/
├── core/
├── users/
├── chat/
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```
- **core/: Handles posts, events, and collaboration tools.**
- **users/: Manages user registration, authentication, and profiles.**
- **chat/: Implements direct messaging and mentorship chat functionalities.**
- **templates/: HTML templates for views.**
- **static/: Static assets like CSS, JS, and images.**
- **media/: User-uploaded files (e.g., profile pictures, creative works).**
   
## Technologies Used
1. Backend: Django (Python)
2. Frontend: HTML, CSS, JavaScript
3. Database: MySql
4. Websockets: Django Channels (for real-time messaging)
   
## Contributing
We welcome contributions! Follow these steps to contribute:

1. Fork the repository.
2. Create a feature branch: "git checkout -b feature-name".
3. Commit changes: "git commit -m "Add feature""
4. Push to your branch: "git push origin feature-name".
5. Submit a pull request.
 
## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For queries or suggestions, please reach out to:
Email: support@youthcreativityhub.com
GitHub: Youth Creativity Hub
