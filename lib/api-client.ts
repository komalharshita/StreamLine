const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseUrl = BASE_URL) {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      'Authorization': 'Bearer mock-session-token-12345',
    };
  }

  async request(path: string, options: RequestInit & { timeout?: number } = {}) {
    const url = `${this.baseUrl}${path}`;
    const { timeout = 20000, headers, ...rest } = options;

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...rest,
        headers: {
          ...this.defaultHeaders,
          ...headers,
        },
        signal: controller.signal,
      });
      clearTimeout(id);

      if (!response.ok) {
        let errData = {};
        try {
          errData = await response.json();
        } catch (_) {}
        
        const apiError = new Error(
          (errData as any)?.detail || response.statusText || 'API Request failed'
        );
        (apiError as any).status = response.status;
        (apiError as any).data = errData;
        throw apiError;
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      return await response.text();
    } catch (error: any) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout exceeded');
      }
      throw error;
    }
  }

  get(path: string, options?: RequestInit & { timeout?: number }) {
    return this.request(path, { ...options, method: 'GET' });
  }

  post(path: string, body?: any, options?: RequestInit & { timeout?: number }) {
    const isFormData = body instanceof FormData;
    const headers: Record<string, string> = {};

    let requestBody: any;
    if (isFormData) {
      requestBody = body;
      // Do not set Content-Type header; browser will automatically set boundary for FormData
    } else {
      headers['Content-Type'] = 'application/json';
      requestBody = body ? JSON.stringify(body) : undefined;
    }

    return this.request(path, {
      ...options,
      method: 'POST',
      body: requestBody,
      headers: {
        ...headers,
        ...options?.headers,
      },
    });
  }
}

export const apiClient = new ApiClient();
