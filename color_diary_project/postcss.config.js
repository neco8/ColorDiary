module.exports = ({ env }) => ({
    plugins: {
        "autoprefixer": env === "production" ? {} : false,
        "cssnano": env === "production" ? {} : false,
        "postcss-normalize": {}
    }
})