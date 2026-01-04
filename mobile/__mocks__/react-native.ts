export const Platform = {
  OS: 'ios',
  select: jest.fn((obj: Record<string, unknown>) => obj.ios ?? obj.default),
};

export default {
  Platform,
};
