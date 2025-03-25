from flask_socketio import SocketIO, join_room, leave_room, emit

class SocketManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置Socket.IO事件处理程序"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """处理连接事件"""
            print('Client connected')
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """处理断开连接事件"""
            print('Client disconnected')
        
        @self.socketio.on('join')
        def handle_join(data):
            """处理加入房间事件"""
            room = data.get('room')
            if room:
                join_room(room)
                emit('status', {'message': f'已加入房间: {room}'}, room=room)
                print(f'Client joined room: {room}')
        
        @self.socketio.on('leave')
        def handle_leave(data):
            """处理离开房间事件"""
            room = data.get('room')
            if room:
                leave_room(room)
                print(f'Client left room: {room}')
        
        @self.socketio.on('message')
        def handle_message(data):
            """处理消息事件"""
            room = data.get('room')
            message = data.get('message')
            if room and message:
                emit('message', {'message': message}, room=room)
                print(f'Message sent to room {room}: {message}') 