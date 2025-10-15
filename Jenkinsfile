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

                    echo "Creating .env file dynamically..."
                        cat > .env << EOF
                        POSTGRES_DB=chapDB
                        POSTGRES_USER=ceelo
                        POSTGRES_PASSWORD=ChApDB_2024!Secur3
                        POSTGRES_HOST=db
                        POSTGRES_PORT=5432
                        DJANGO_SETTINGS_MODULE=config.settings.development
                        EOF
                            
                        echo "Verifying .env file was created:"
                        ls -la .env
                        cat .env

                    echo "Building images using Minikube's Docker daemon..."
                    eval $(minikube docker-env)
                                        
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