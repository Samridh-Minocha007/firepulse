🎜️ FirePulse+ - AI-Powered Entertainment Hub

Your All-In-One AI Companion for Movie Discovery, Trivia & Watch Parties

🚀 Features

🎞️ Smart Movie & Music Recommendations<br>
Powered by Google Gemini Pro<br>
Tailored suggestions based on mood, time, actor, director, or genre<br>
Analyzes your watch history & Google Calendar events<br>

🤖 AI Trivia Game<br>
Generates unique questions based on your interests<br>
Tracks scores and awards badges for milestones<br>

💬 Live Watch Parties<br>
Real-time rooms powered by WebSockets<br>
Suggests a movie for the group and launches a video meet in one click<br>

📅 Google Calendar Integration<br>
Links with your Google Calendar<br>
Recommends movies for parties, holidays, and other events<br>

📄 Watch Logging & Personalized History<br>
Stores your watched movies<br>
Recommends new ones tailored to your taste<br>

🧰 Tech Stack<br>

🖥️ Frontend<br>
React<br>
Vite<br>
Tailwind CSS<br>

🔧 Backend<br>
FastAPI (Python)<br>
WebSockets for real-time sessions<br>

🗃️ Database<br>
PostgreSQL<br>
SQLAlchemy<br>
Alembic<br>

🔐 Authentication<br>
OAuth 2.0 (Google Login)<br>
JWT Tokens<br>

🌐 APIs<br>
Google Gemini<br>
TMDB<br>
Spotify<br>
Google Calendar<br>

☁️ DevOps & Deployment<br>
AWS Amplify (Frontend)<br>
AWS Lambda (Backend)<br>
Docker (Containerization)<br>

🧠 AI Assistant "Alex" Recommending Movies\Songs

![Movie Suggestions](assets/movie-suggestions.png)

![Movie Suggestions](assets/movie-suggestions(by-mood).png)

![Movie Suggestions](assets/song-suggestions.png)

⏱️Time Based Suggestions

![Movie Suggestions](assets/time-based-recommendations.png)

✅History Based Suggestions

![Movie Suggestions](assets/history-based-recommendations.png)

🎉 Personalized AI Trivia Game 

![Movie Suggestions](assets/trivia-1.png)

![Movie Suggestions](assets/trivia-2.png)

![Movie Suggestions](assets/trivia-3.png)

🎃 Calendar-Integrated Movie Suggestions

![Movie Suggestions](assets/calendar-based.png)

📽 Live Watch Party with AI Suggestions

![Movie Suggestions](assets/watch-party.png)

![Movie Suggestions](assets/Connection-established-1.png)

![Movie Suggestions](assets/Connection-established-2.png)

![Movie Suggestions](assets/Live-chat.png)

![Movie Suggestions](assets/Group-based-movie-suggestion.png)

![Movie Suggestions](assets/Meet-link.png)

# RUN LOCALLY
# Frontend
cd frontend<br>
npm install<br>
npm run dev<br>

# Backend
cd firepulse<br>
pip install -r requirements.txt<br>
uvicorn main:app --reload<br>

#For .env
TMDB_API_KEY=your_key
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
GOOGLE_API_KEY=your_api_key
JWT_SECRET_KEY=your_key
JWT_ALGORITHM=your_key
GOOGLE_CLIENT_ID: str=your_key
GOOGLE_CLIENT_SECRET=your_key
GOOGLE_REDIRECT_URI=your_key

📅 Author
Samridh Minocha
📧 samridhminocha2005@gmail.com
