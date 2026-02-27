#!/bin/bash
# MCP Server 启动脚本

MCP_DIR="/root/.openclaw/workspace/mcp"
CONFIG_FILE="$MCP_DIR/server-config.json"
PID_FILE="$MCP_DIR/server.pid"
LOG_FILE="$MCP_DIR/server.log"

# 默认端口
PORT=${MCP_PORT:-3000}

cd "$MCP_DIR" || exit 1

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "MCP Server is already running (PID: $(cat $PID_FILE))"
        exit 1
    fi
    
    echo "Starting MCP Server on port $PORT..."
    nohup python3 server.py "$CONFIG_FILE" "$PORT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    # 等待启动
    sleep 2
    
    if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✅ MCP Server started successfully (PID: $(cat $PID_FILE))"
        echo "   Health check: http://localhost:$PORT/health"
        echo "   SSE endpoint: http://localhost:$PORT/sse"
        echo "   Log file: $LOG_FILE"
    else
        echo "❌ Failed to start MCP Server"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "MCP Server is not running"
        exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    echo "Stopping MCP Server (PID: $PID)..."
    
    if kill "$PID" 2>/dev/null; then
        # 等待进程结束
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # 强制结束
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo "✅ MCP Server stopped"
    else
        echo "❌ Failed to stop MCP Server"
        exit 1
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "MCP Server is running (PID: $(cat $PID_FILE))"
        
        # 检查健康状态
        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            echo "✅ Health check passed"
            curl -s http://localhost:$PORT/health | python3 -m json.tool 2>/dev/null || true
        else
            echo "⚠️ Health check failed"
        fi
    else
        echo "MCP Server is not running"
        rm -f "$PID_FILE"
    fi
}

restart() {
    stop
    sleep 1
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
