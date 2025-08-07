#!/bin/bash

# Wakili Quick Docker Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your actual values before deploying."
        else
            print_error ".env.example file not found. Please create a .env file manually."
            exit 1
        fi
    fi
}

# Function to build and start services
deploy_production() {
    print_status "Deploying production services..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    print_success "Production services deployed successfully!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:3000"
    print_status "API Docs: http://localhost:8000/docs"
}

# Function to deploy development services
deploy_development() {
    print_status "Deploying development services..."
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.dev.yml build --no-cache
    docker-compose -f docker-compose.dev.yml up -d
    print_success "Development services deployed successfully!"
    print_status "Backend: http://localhost:8000 (with hot reload)"
    print_status "Frontend: http://localhost:3000 (with hot reload)"
    print_status "API Docs: http://localhost:8000/docs"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    print_success "All services stopped"
}

# Function to view logs
view_logs() {
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "Service Status:"
    echo ""
    echo "Production Services:"
    docker-compose ps
    echo ""
    echo "Development Services:"
    docker-compose -f docker-compose.dev.yml ps
}

# Function to show help
show_help() {
    echo "Wakili Quick Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  prod          Deploy production services"
    echo "  dev           Deploy development services"
    echo "  stop          Stop all services"
    echo "  logs [dev]    View logs (add 'dev' for development services)"
    echo "  status        Show service status"
    echo "  cleanup       Clean up Docker resources"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 prod       # Deploy production"
    echo "  $0 dev        # Deploy development"
    echo "  $0 logs dev   # View development logs"
}

# Main script logic
main() {
    case "${1:-help}" in
        "prod")
            check_docker
            check_env
            deploy_production
            ;;
        "dev")
            check_docker
            check_env
            deploy_development
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            view_logs "$2"
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"