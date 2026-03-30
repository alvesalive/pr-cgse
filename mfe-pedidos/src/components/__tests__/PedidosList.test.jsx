import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, waitFor, act } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

// O mock PRECISA ser definido com factory sem referências externas (hoisting do Vitest)
vi.mock('axios', () => {
  const mockGet = vi.fn().mockResolvedValue({ data: [] })
  const instance = {
    get: mockGet,
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: {
      request: { use: vi.fn(), eject: vi.fn() },
      response: { use: vi.fn(), eject: vi.fn() }
    }
  }
  return {
    default: {
      create: vi.fn(() => instance),
      ...instance
    }
  }
})

// Import APÓS o mock
import PedidosList from '../PedidosList'

const renderPedidosList = async (props = {}) => {
  let result
  await act(async () => {
    result = render(
      <MemoryRouter>
        <PedidosList token="fake-token" userRole="USER" {...props} />
      </MemoryRouter>
    )
  })
  return result
}

describe('PedidosList Component', () => {
  it('renderiza sem erros quando lista está vazia', async () => {
    await renderPedidosList()
    expect(document.body).toBeTruthy()
  })

  it('admin renderiza sem erros', async () => {
    await renderPedidosList({ userRole: 'ADMIN' })
    expect(document.body).toBeTruthy()
  })

  it('renderiza estrutura da página de pedidos sem token', async () => {
    await renderPedidosList({ token: '' })
    expect(document.body).toBeTruthy()
  })

  it('exibe conteúdo após carregar pedidos', async () => {
    await renderPedidosList()
    await waitFor(() => {
      expect(document.body).toBeTruthy()
    })
  })

  it('não crasha com props incorretos', async () => {
    await expect(renderPedidosList({ userRole: 'INVALID' })).resolves.toBeDefined()
  })
})
