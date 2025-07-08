# test_ws.py
import asyncio
import websockets
import sys

# --- This function will handle sending messages ---
async def send_messages(websocket):
    print("You can now type messages and press Enter to send.")
    print("Type 'suggest_movie' to get a group recommendation, or 'quit' to exit.")
    loop = asyncio.get_event_loop()
    while True:
        message = await loop.run_in_executor(None, sys.stdin.readline)
        message = message.strip()
        if message == 'quit':
            break
        await websocket.send(message)

# --- This function will handle receiving messages ---
async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"< Received: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection to server closed.")

# --- Main function to connect and run tasks ---
async def test_websocket(party_id, user_id):
    uri = f"ws://localhost:8000/api/v1/ws/{party_id}/{user_id}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"--- Connected as '{user_id}' to party '{party_id}' ---")
            
            # Run sending and receiving tasks concurrently
            send_task = asyncio.create_task(send_messages(websocket))
            receive_task = asyncio.create_task(receive_messages(websocket))
            
            await asyncio.gather(send_task, receive_task)

    except Exception as e:
        print(f"Error: Could not connect to {uri}. Is the server running?")
        print(e)

if __name__ == "__main__":
    # --- Instructions ---
    # To run this script:
    # 1. Open a terminal.
    # 2. Run: python test_ws.py movie_night sam
    # 3. Open a SECOND terminal.
    # 4. Run: python test_ws.py movie_night jessica
    
    if len(sys.argv) < 3:
        print("Usage: python test_ws.py <party_id> <user_id>")
    else:
        party = sys.argv[1]
        user = sys.argv[2]
        asyncio.run(test_websocket(party, user))