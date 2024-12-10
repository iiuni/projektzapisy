import { shallowMount } from '@vue/test-utils'
import axios from 'axios'
import NotificationsComponent from './Widget.vue'

jest.mock('axios');

describe('NotificationsComponent', () => {
  let wrapper;

  beforeEach(() => {
    axios.get.mockResolvedValue({
      data: [
        { id: '1', description: 'Test notification', 'issued_on': '2024-12-03T10:00:00Z', 'target': 'some target' },
        { id: '2', description: 'Another notification', 'issued_on': '2024-12-02T10:00:00Z', 'target': 'some other target' }
      ],
    });
    wrapper = shallowMount(NotificationsComponent);
  });

  it('should delete notification from n_list when executing deleteOne method', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.n_list).toHaveLength(2);
    axios.post.mockResolvedValue({
      data: [{ id: '2', description: 'Another notification', 'issued_on': '2024-12-02T10:00:00Z', 'target': 'some other target' }],
    });
    await wrapper.vm.deleteOne('1');
    await wrapper.vm.$nextTick();
    expect(axios.post).toHaveBeenCalledWith('/notifications/delete', { uuid: '1' });
    expect(wrapper.vm.n_list).toHaveLength(1);
    expect(wrapper.vm.n_list[0].id).toBe('2');
  })
})