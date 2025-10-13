import torch


def scaling_M(M: torch.FloatTensor, m_q_shift_limit=32):
    assert torch.all(M > 0), "M should be positive"

    M = torch.round(M * 10**5) / 10**5
    m_q_shift = torch.tensor(1, dtype=torch.int32)

    while m_q_shift.item() < m_q_shift_limit:
        # compute shift as Python int to avoid int32 overflow when 2**shift becomes >= 2**31
        shift = int(m_q_shift.item())
        mult = 2 ** shift
        m_q = torch.round(M * mult).to(torch.int32)

        # use float inverse power for error computation
        error = (M - m_q * (2 ** (-shift))) / M
        if torch.all(error > 0.0001) or torch.all(error < 0):
            m_q_shift += 1
        else:
            break
    return m_q_shift, m_q
