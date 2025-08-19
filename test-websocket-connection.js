// WebSocket连接测试脚本
const WebSocket = require('ws');

// 测试WebSocket连接
function testWebSocketConnection() {
    console.log('开始测试WebSocket连接...');
    
    const wsUrl = 'ws://127.0.0.1:8000/ws/permissions/anonymous';
    console.log(`连接到: ${wsUrl}`);
    
    const ws = new WebSocket(wsUrl);
    
    ws.on('open', function open() {
        console.log('✅ WebSocket连接成功建立');
        
        // 发送连接消息
        const connectMessage = {
            type: 'connect',
            data: { userId: null },
            timestamp: Date.now()
        };
        
        ws.send(JSON.stringify(connectMessage));
        console.log('📤 发送连接消息:', connectMessage);
    });
    
    ws.on('message', function message(data) {
        try {
            const parsedData = JSON.parse(data.toString());
            console.log('📥 收到服务器消息:', parsedData);
            
            if (parsedData.type === 'connection_confirmed') {
                console.log('✅ 连接确认成功');
                console.log('用户ID:', parsedData.user_id);
                console.log('服务器时间:', parsedData.server_time);
                console.log('可用功能:', parsedData.features);
                
                // 测试心跳
                setTimeout(() => {
                    const heartbeatMessage = {
                        type: 'heartbeat',
                        timestamp: Date.now()
                    };
                    ws.send(JSON.stringify(heartbeatMessage));
                    console.log('💓 发送心跳消息');
                }, 1000);
                
                // 5秒后关闭连接
                setTimeout(() => {
                    console.log('🔚 测试完成，关闭连接');
                    ws.close();
                }, 5000);
            }
        } catch (error) {
            console.error('❌ 解析消息失败:', error);
        }
    });
    
    ws.on('close', function close(code, reason) {
        console.log(`🔌 WebSocket连接已关闭 - 代码: ${code}, 原因: ${reason}`);
    });
    
    ws.on('error', function error(err) {
        console.error('❌ WebSocket连接错误:', err.message);
    });
}

// 运行测试
testWebSocketConnection();