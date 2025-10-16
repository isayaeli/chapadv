pipeline {
    agent any
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                sh 'ls -la'  // Verify files are there
            }
        }
        
        stage('Verify Required Files') {
            steps {
                sh '''
                    echo "Checking for required files..."
                    [ -f Dockerfile ] || { echo "Dockerfile missing!"; exit 1; }
                    [ -f docker-compose.yml ] || { echo "docker-compose.yml missing!"; exit 1; }
                    [ -f requirements.txt ] || { echo "requirements.txt missing!"; exit 1; }
                    echo "✅ All required files present"
                '''
            }
        }
        
       
        stage('Build and Run') {
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
                ])
                
                 {

                sh '''
                    # Check if rebuild is needed
                    if [ -f requirements.txt ] && [ requirements.txt -nt .last_build ]; then
                        echo "📦 Dependencies changed - rebuilding image..."
                        docker-compose down || true
                        docker-compose build
                    else
                        echo "⚡ No dependency changes - using existing image"
                    fi
                    
                    echo "🚀 Starting containers..."
                    docker-compose up -d
                    
                    # Update build timestamp
                    touch .last_build
                    
                    echo "Waiting for app to start..."
                    sleep 10
                '''
                }
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking if app is healthy..."
                    curl -f http://localhost:8000/health || curl -f http://localhost:8000/admin/ || exit 1
                    echo "✅ App is running successfully!"
                '''
            }
        }


    }
    
    post {
        always {
            echo "Pipeline completed"
        }
        success {
            echo "🚀 Django app is running at: http://localhost:8000"
        }
        failure {
            echo "❌ Pipeline failed. Check the logs above for details."
        }
    }
}