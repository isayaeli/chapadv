pipeline {
    agent any
    
    environment {
        KUBECONFIG = "${env.HOME}/.kube/config"
        COMPOSE_PROJECT_NAME = "chapadv-app-${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build and Test with Compose') {
            steps {
                sh '''
                    echo "Building and testing with Docker Compose..."

                     # Load environment variables FIRST
                    echo "Loading environment variables..."
                    if [ -f .env ]; then
                        export $(cat .env | grep -v '^#' | xargs)
                        echo "Environment variables loaded from .env file"
                    else
                        echo "No .env file found, using default environment variables"
                    fi
                    
                    # Build images
                    docker-compose build
                    
                    # Run tests
                    docker-compose run --rm web python manage.py test
                    
                    # Run migrations in test environment
                    docker-compose run --rm web python manage.py migrate
                    
                    # Load image to Minikube
                    minikube image load chapadv-app:latest
                '''
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                sh '''
                    echo "Deploying to Kubernetes..."
                    kubectl apply -k k8s/  # Apply entire k8s directory
                    kubectl wait --for=condition=ready pod -l app=chapadv-app --timeout=300s
                '''
            }
        }
        
        stage('K8s Migrations') {
            steps {
                sh '''
                    # Run migrations in Kubernetes
                    POD_NAME=$(kubectl get pods -l app=chapadv-app -o jsonpath="{.items[0].metadata.name}")
                    kubectl exec $POD_NAME -- python manage.py migrate
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    SERVICE_URL=$(minikube service chapadv-service --url)
                    curl -f $SERVICE_URL/health/ || exit 1
                    echo "✅ Health check passed!"
                '''
            }
        }
    }
    
    post {
        always {
            // Cleanup Docker Compose resources
            sh 'docker-compose down --remove-orphans || true'
            sh '''
                kubectl get pods
                echo "--- Services ---"
                kubectl get services
            '''
        }
        success {
            sh '''
                echo "✅ Pipeline completed successfully!"
                echo "🌐 Access your app at: $(minikube service django-service --url)"
            '''
        }
        failure {
            echo "❌ Pipeline failed. Check the logs above for details."
        }
    }
}