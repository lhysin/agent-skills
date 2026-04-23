# Test Template

## OrderServiceTest.java

```java
package {$ROOT}.domain.order.service;

import {$ROOT}.domain.order.dto.OrderDto;
import {$ROOT}.domain.order.entity.Order;
import {$ROOT}.domain.order.repository.OrderRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @InjectMocks
    private OrderService orderService;

    @BeforeEach
    void setUp() {
    }

    @Test
    void findAll_ShouldReturnOrders() {
        // given
        Order order = Order.builder()
            .id(1L)
            .productName("Test Product")
            .quantity(10)
            .price(1000L)
            .build();
        when(orderRepository.findAll()).thenReturn(List.of(order));

        // when
        List<OrderDto> result = orderService.findAll();

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).productName()).isEqualTo("Test Product");
    }

    @Test
    void findById_WhenOrderExists_ShouldReturnOrder() {
        // given
        Order order = Order.builder()
            .id(1L)
            .productName("Test Product")
            .quantity(10)
            .price(1000L)
            .build();
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));

        // when
        OrderDto result = orderService.findById(1L);

        // then
        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.productName()).isEqualTo("Test Product");
    }

    @Test
    void save_ShouldReturnSavedOrder() {
        // given
        OrderDto dto = OrderDto.builder()
            .productName("New Product")
            .quantity(5)
            .price(500L)
            .build();
        Order savedOrder = Order.builder()
            .id(1L)
            .productName("New Product")
            .quantity(5)
            .price(500L)
            .build();
        when(orderRepository.save(any(Order.class))).thenReturn(savedOrder);

        // when
        OrderDto result = orderService.save(dto);

        // then
        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.productName()).isEqualTo("New Product");
    }
}
```