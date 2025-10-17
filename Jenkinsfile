pipeline {
    agent any

    environment {
        // Kubeconfig file stored as a Jenkins "Secret file"
        KUBECONFIG = credentials('Kube-id')
        DOCKER_IMAGE = "ceelo/chapadv:latest"
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

        stage('Build & Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                        echo "🐳 Logging in to Docker Hub..."
                        echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin

                        # Rebuild only if requirements.txt or Dockerfile changed
                        if [ requirements.txt -nt .last_build ] || [ Dockerfile -nt .last_build ]; then
                            echo "📦 Dependencies or Dockerfile changed - rebuilding image..."
                            docker-compose down || true
                            docker-compose build

                            echo "☁️ Tagging and pushing image to Docker Hub..."
                            docker tag chapadv_web:latest $DOCKER_IMAGE
                            docker push $DOCKER_IMAGE

                            # Update build timestamp
                            touch .last_build
                        else
                            echo "⚡ No changes detected - skipping build and push"
                        fi
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
                    # Make sure deployment uses Docker Hub image
                    kubectl set image deployment/chapadv chapadv=$DOCKER_IMAGE --record || kubectl apply -k k8s/

                    echo "⏳ Waiting for deployment rollout..."
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
