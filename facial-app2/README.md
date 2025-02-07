# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

to install the project
```
pnpm install
pnpm build
```

using nginx for the deployment
example nginx config
```
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    root /path/to/your/vite-project/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    error_page 404 /404.html;
    location = /404.html {
        internal;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        internal;
    }
}
```

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh
