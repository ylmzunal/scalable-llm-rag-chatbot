import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html>
      <Head>
        {/* Meta tags for CORS */}
        <meta httpEquiv="Access-Control-Allow-Origin" content="*" />
        <meta httpEquiv="Access-Control-Allow-Methods" content="GET, POST, PUT, DELETE, OPTIONS" />
        <meta httpEquiv="Access-Control-Allow-Headers" content="Origin, X-Requested-With, Content-Type, Accept" />
        {/* Other meta tags */}
        <meta name="description" content="RAG Chatbot for Kubernetes Demo" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
} 