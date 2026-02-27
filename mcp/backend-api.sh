#!/bin/bash
# MCP Backend API 启动脚本

MCP_DIR="/root/.openclaw/workspace/mcp"
PID_FILE="$MCP_DIR/backend_api.pid"
LOG_FILE="$MCP_DIR/backend_api.log"

# 默认配置
MCP_SERVER=${MCP_SERVER:-http://localhost:3000}
PORT=${API_PORT:-8080}

cd "$MCP_DIR" || exit 1

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "MCP Backend API is already running (PID: $(cat $PID_FILE))"
        exit 1
    fi
    
    echo "Starting MCP Backend API on port $PORT..."
    echo "MCP Server: $MCP_SERVER"
    
    nohup python3 backend_api.py --mcp-server "$MCP_SERVER" --port "$PORT" > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
    
    # 等待启动
    sleep 3
    
    if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✅ MCP Backend API started successfully (PID: $(cat $PID_FILE))"
        echo "   API endpoint: http://localhost:$PORT"
        echo "   Health check: http://localhost:$PORT/api/health"
        echo "   Log file: $LOG_FILE"
    else
        echo "❌ Failed to start MCP Backend API"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "MCP Backend API is not running"
        exit 1
    fi
    
    PID=$(cat "$PID_FILE")
    echo "Stopping MCP Backend API (PID: $PID)..."
    
    if kill "$PID" 2>/dev/null; then
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo "✅ MCP Backend API stopped"
    else
        echo "❌ Failed to stop MCP Backend API"
        exit 1
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "MCP Backend API is running (PID: $(cat $PID_FILE))"
        
        if curl -s http://localhost:$PORT/api/health > /dev/null 2>&1; then
            echo "✅ Health check passed"
            curl -s http://localhost:$PORT/api/health | python3 -m json.tool 2>/dev/null || true
        else
            echo "⚠️ Health check failed"
        fi
    else
        echo "MCP Backend API is not running"
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
