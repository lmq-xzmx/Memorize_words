const WebSocket = require('ws');

console.log('开始WebSocket连接测试...');

const ws = new WebSocket('ws://127.0.0.1:8000/ws/permissions/anonymous/');

ws.on('open', function open() {
    console.log('✅ WebSocket连接已建立');
    
    // 发送连接消息
    const connectMessage = {
        type: 'connect',
        timestamp: Date.now()
    };
    
    console.log('📤 发送连接消息:', connectMessage);
    ws.send(JSON.stringify(connectMessage));
    
    // 等待2秒后发送心跳
    setTimeout(() => {
        const heartbeatMessage = {
            type: 'heartbeat',
            timestamp: Date.now()
        };
        
        console.log('💓 发送心跳消息:', heartbeatMessage);
        ws.send(JSON.stringify(heartbeatMessage));
    }, 2000);
});

ws.on('message', function message(data) {
    try {
        const parsed = JSON.parse(data.toString());
        console.log('📥 收到消息:', parsed);
    } catch (e) {
        console.log('📥 收到原始消息:', data.toString());
    }
});

ws.on('close', function close(code, reason) {
    console.log('❌ WebSocket连接已关闭');
    console.log('关闭代码:', code);
    console.log('关闭原因:', reason.toString());
});

ws.on('error', function error(err) {
    console.log('🚨 WebSocket错误:', err.message);
});

// 10秒后主动关闭连接
setTimeout(() => {
    console.log('⏰ 10秒测试完成，主动关闭连接');
    ws.close();
    process.exit(0);
}, 10000);