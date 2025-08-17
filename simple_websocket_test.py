#!/usr/bin/env python
"""
简单的WebSocket连接测试
测试WebSocket是否能正确建立连接
"""

import asyncio
import websockets
import json
from urllib.parse import urlencode

async def test_websocket_basic():
    """
    测试基本WebSocket连接
    """
    print("🚀 开始基本WebSocket连接测试...")
    
    # 测试不带任何参数的连接
    uri = "ws://localhost:8001/ws/permissions/"
    print(f"🔗 连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功建立")
            
            # 发送一个简单的消息
            test_message = {
                "type": "heartbeat",
                "timestamp": "test"
            }
            await websocket.send(json.dumps(test_message))
            print("📤 发送测试消息")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 收到响应: {response}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时")
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")

async def test_websocket_with_fake_token():
    """
    测试带假token的WebSocket连接
    """
    print("\n🚀 开始带假token的WebSocket连接测试...")
    
    # 使用假token
    fake_token = "fake_token_123"
    params = urlencode({"token": fake_token, "userId": "1"})
    uri = f"ws://localhost:8001/ws/permissions/?{params}"
    print(f"🔗 连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功建立")
            
            # 发送一个简单的消息
            test_message = {
                "type": "heartbeat",
                "timestamp": "test"
            }
            await websocket.send(json.dumps(test_message))
            print("📤 发送测试消息")
            
            # 等待响应
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 收到响应: {response}")
            except asyncio.TimeoutError:
                print("⏰ 等待响应超时")
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"错误类型: {type(e).__name__}")

async def main():
    """
    主测试函数
    """
    await test_websocket_basic()
    await test_websocket_with_fake_token()
    print("\n📊 测试完成")

if __name__ == "__main__":
    asyncio.run(main())