# Image Labeler

A React-based image labeling platform with support for hierarchical categories, built with Vite, TypeScript, and TailwindCSS.

## Features

- Upload and label multiple images
- Hierarchical category system
- CSV export functionality
- Progress auto-save
- Responsive design
- Docker support
- GitHub Pages deployment

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd image-labeler
```

2. Build and start the container:
```bash
docker-compose up --build
```

3. Access the application at `http://localhost:5173`

### Development with Docker

The Docker setup includes:
- Hot reloading support
- Volume mounting for source code
- Development dependencies
- Proper port exposure

Docker commands:
```bash
# Start development server
docker-compose up

# Rebuild container after dependencies change
docker-compose up --build

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
```

## Local Development

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

4. Preview production build:
```bash
npm run preview
```

## GitHub Pages Deployment

The application is automatically deployed to GitHub Pages when pushing to the `labelling` branch.

### Manual Deployment

1. Build the application:
```bash
npm run build
```

2. Push to the labelling branch:
```bash
git checkout labelling
git add .
git commit -m "Update build"
git push origin labelling
```

The GitHub Actions workflow will automatically:
- Build the application
- Deploy to GitHub Pages
- Cache dependencies for faster builds

## Project Structure

```
image-labeler/
├── src/
│   ├── components/
│   │   └── ImageLabeler/
│   ├── types/
│   ├── utils/
│   └── list.json
├── public/
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:
```env
VITE_APP_TITLE=Image Labeler
# Add any other environment variables here
```

### Docker Environment

The Docker environment uses the following ports:
- Development: 5173
- Preview: 4173

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
