pipeline {
    agent any

    environment {
        // Kubeconfig file stored as a Jenkins "Secret file"
        KUBECONFIG = credentials('Kube-id')
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                echo "🔄 Checking out code..."
                checkout scm
                sh 'ls -la'  // Verify files are present
            }
        }

        stage('Verify Required Files') {
            steps {
                echo "📂 Verifying required files..."
                sh '''
                    [ -f Dockerfile ] || { echo "❌ Dockerfile missing!"; exit 1; }
                    [ -f docker-compose.yml ] || { echo "❌ docker-compose.yml missing!"; exit 1; }
                    [ -f requirements.txt ] || { echo "❌ requirements.txt missing!"; exit 1; }
                    # Create .last_build if it doesn't exist
                    [ -f .last_build ] || touch .last_build
                    echo "✅ All required files present"
                '''
            }
        }

        stage('Build and Run Docker') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'postgres-db-credentials', 
                        usernameVariable: 'POSTGRES_USER', 
                        passwordVariable: 'POSTGRES_PASSWORD'
                    ),
                    string(
                        credentialsId: 'postgres-db-name', 
                        variable: 'POSTGRES_DB'
                    )
                ]) {
                    sh '''
                        export POSTGRES_HOST="db"
                        export POSTGRES_PORT="5432"

                        # Rebuild only if requirements.txt changed
                        if [ requirements.txt -nt .last_build ]; then
                            echo "📦 Dependencies changed - rebuilding image..."
                            docker-compose down || true
                            docker-compose build
                        else
                            echo "⚡ No dependency changes - using existing image"
                        fi

                        echo "🚀 Starting Docker containers..."
                        docker-compose up -d

                        # Update build timestamp
                        touch .last_build

                        echo "⏳ Waiting for app to start..."
                        sleep 10
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                echo "🔍 Performing health check..."
                sh '''
                    retries=5
                    until curl -f http://localhost:8000/health || curl -f http://localhost:8000/admin/; do
                        retries=$((retries-1))
                        if [ $retries -le 0 ]; then
                            echo "❌ App failed health check"
                            exit 1
                        fi
                        echo "⚡ Waiting for app to be ready..."
                        sleep 5
                    done
                    echo "✅ App is running successfully!"
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo "🚀 Deploying to Kubernetes..."
                sh '''
                

                    # Build Docker image for Kubernetes
                    docker build -t chapadv:latest .

                    # Deploy with kustomize/k8s manifests
                    kubectl apply -k k8s/

                    # Wait for deployment rollout
                    kubectl rollout status deployment/chapadv

                    echo "✅ chapadv successfully rolled out to Kubernetes!"
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
        success {
            echo "🚀 Django app is running at: http://localhost:8000"
        }
        failure {
            echo "❌ Pipeline failed. Check logs above."
        }
    }
}
